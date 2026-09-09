"""
ISPPV1 2026
Study Case: Ultimate Fantasy (RPG)

Author: Eugenio Montilla
eugeniorusso1411@gmail.com

This file contains the class TakeTurnState: drives a single entity's turn.
"""

import math
import random
from typing import Any, Optional, Dict

import pygame

from gale.state import BaseState
from gale.timer import Timer

import settings


class TakeTurnState(BaseState):
    def enter(self, battle_state: Any, entity: Any) -> None:
        self.battle_state = battle_state
        self.entity = entity
        self.enemy_attacks_in_a_row = 0
        
        if self.entity in self.battle_state.party.characters.values():
            self._take_party_turn()
        else:
            self._take_enemy_turn()

    def _party_keys(self):
        return sorted(self.battle_state.party.characters.keys())

    # -- party turns ---------------------------------------------------

    def _take_party_turn(self) -> None:
        if self.entity.dead:
            self.state_machine.pop()
            return

        index = list(self.battle_state.party.characters.values()).index(self.entity)
        self.battle_state.party_status_view.selected_index = index

        from src.states.game.BattleMessageState import BattleMessageState

        self.state_machine.push(
            BattleMessageState(self.state_machine),
            battle_state=self.battle_state,
            message=f"Turn for {self.entity.name}! Select an action.",
            on_close=self._prompt_action,
        )

    def _prompt_action(self) -> None:
        from src.states.game.SelectActionState import SelectActionState

        def on_action_selected(action: Optional[Dict[str, Any]] = None) -> None:
            if action and action["name"] == "Run":
                self._run()
                return

            if action and "wait_time" in action:
                self.entity.max_wait_time = action["wait_time"]
                self.entity.wait_time = action["wait_time"]
            else:
                self.entity.max_wait_time = 0.4
                self.entity.wait_time = 0.4

            if all(enemy.dead for enemy in self.battle_state.enemies):
                self._victory()
            else:
                self.state_machine.pop()

        self.state_machine.push(
            SelectActionState(self.state_machine),
            battle_state=self.battle_state,
            entity=self.entity,
            on_action_selected=on_action_selected,
        )

    def _run(self) -> None:
        from src.states.game.BattleMessageState import BattleMessageState
        from src.states.game.FadeOutState import FadeOutState
        from src.states.game.FadeInState import FadeInState

        def fade_in_complete() -> None:
            self.state_machine.pop()
            self.state_machine.pop()
            self.state_machine.push(
                FadeOutState(self.state_machine),
                color=(255, 255, 255),
                time=1,
                on_complete=lambda: None,
            )

        def message_close() -> None:
            self.state_machine.push(
                FadeInState(self.state_machine),
                color=(255, 255, 255),
                time=1,
                on_complete=fade_in_complete,
            )

        self.state_machine.push(
            BattleMessageState(self.state_machine),
            battle_state=self.battle_state,
            message="Got away safely!",
            on_close=message_close,
        )

    # -- enemy turns ----------------------------------------------------

    def _take_enemy_turn(self) -> None:
        if self.entity.dead:
            self.state_machine.pop()
            return

        action = random.choice(self.entity.actions)

        if action["target_type"] == "enemy":
            targets = list(self.battle_state.party.characters.values())
            target_label = "you"
        else:
            targets = self.battle_state.enemies
            target_label = "them"

        if action["require_target"]:
            alive = [target for target in targets if not target.dead]
            target = random.choice(alive)
            amount = action["func"](self.entity, target, action.get("strength"))
            settings.SOUNDS[action["sound_effect"]].play()
            Timer.tween(0.5, [(target.energy_bar, {"value": target.current_hp})])
            message = f"{self.entity.name} used {action['name']} for {amount} HP on {target.name}."
        else:
            alive_targets = [target for target in targets if not target.dead]
            amount = action["func"](self.entity, alive_targets, action.get("strength"))
            settings.SOUNDS[action["sound_effect"]].play()

            for target in alive_targets:
                Timer.tween(0.5, [(target.energy_bar, {"value": target.current_hp})])

            message = (
                f"{self.entity.name} used {action['name']} for {amount} HP on all of "
                f"{target_label}."
            )

        if all(character.dead for character in self.battle_state.party.characters.values()):
            self._faint()
            return

        from src.states.game.BattleMessageState import BattleMessageState

        def on_message_close() -> None:
            if "wait_time" in action:
                self.entity.max_wait_time = action["wait_time"]
                self.entity.wait_time = action["wait_time"]
            else:
                self.entity.max_wait_time = 3.0
                self.entity.wait_time = 3.0
                
            self.state_machine.pop()

        self.state_machine.push(
            BattleMessageState(self.state_machine),
            battle_state=self.battle_state,
            message=message,
            on_close=on_message_close,
        )

    # -- victory / experience --------------------------------------------

    def _victory(self) -> None:
        settings.stop_music("battle")
        self._victory_channel = settings.SOUNDS["victory"].play(loops=-1)

        from src.states.game.BattleMessageState import BattleMessageState

        self.state_machine.push(
            BattleMessageState(self.state_machine),
            battle_state=self.battle_state,
            message="Victory!",
            on_close=self._start_exp,
        )

    def _start_exp(self) -> None:
        total_level = sum(enemy.level for enemy in self.battle_state.enemies)
        num_characters = len(self.battle_state.party.characters)
        opponent_level = total_level / num_characters
        self._inc_exp(0, opponent_level)

    def _inc_exp(self, index: int, opponent_level: float) -> None:
        keys = self._party_keys()

        if index >= len(keys):
            self._fade_out()
            return

        character = self.battle_state.party.characters[keys[index]]

        if character.dead:
            self._inc_exp(index + 1, opponent_level)
            return

        exp = math.ceil(
            (character.hpiv + character.attackiv + character.defenseiv + character.magiciv)
            * opponent_level
        )

        from src.states.game.BattleMessageState import BattleMessageState

        self.state_machine.push(
            BattleMessageState(self.state_machine),
            battle_state=self.battle_state,
            message=f"{character.name} earned {exp} experience points!",
            on_close=None,
            can_input=False,
        )
        Timer.after(1.5, lambda: self._apply_exp(character, exp, index, opponent_level))

    def _apply_exp(
        self, character: Any, exp: int, index: int, opponent_level: float
    ) -> None:
        settings.SOUNDS["exp"].play()
        new_value = min(character.current_exp + exp, character.exp_to_level)
        Timer.tween(
            0.5,
            [(character.exp_bar, {"value": new_value})],
            on_finish=lambda: self._exp_applied(character, exp, index, opponent_level),
        )

    def _exp_applied(
        self, character: Any, exp: int, index: int, opponent_level: float
    ) -> None:
        self.state_machine.pop()
        character.current_exp += exp

        if character.current_exp >= character.exp_to_level:
            settings.SOUNDS["levelup"].play()
            character.current_exp -= character.exp_to_level
            last_level = character.level
            increases = character.level_up()
            hp_increase = increases[0]
            Timer.tween(
                0.5, [(character.energy_bar, {"value": character.current_hp - hp_increase})]
            )

            from src.states.game.BattleMessageState import BattleMessageState

            message = (
                f"Congratulations! {character.name} advanced from level "
                f"{last_level} level {character.level}!"
            )
            self.state_machine.push(
                BattleMessageState(self.state_machine),
                battle_state=self.battle_state,
                message=message,
                on_close=lambda: self._show_stats(character, increases, index, opponent_level),
            )
        else:
            self._inc_exp(index + 1, opponent_level)

    def _show_stats(self, character: Any, increases: Any, index: int, opponent_level: float) -> None:
        from src.states.game.StatsMenuState import StatsMenuState

        self.state_machine.push(
            StatsMenuState(self.state_machine),
            character=character,
            stats=increases,
            on_close=lambda: self._inc_exp(index + 1, opponent_level),
        )

    def _fade_out(self) -> None:
        if self._victory_channel is not None:
            self._victory_channel.stop()

        from src.states.game.FadeInState import FadeInState
        from src.states.game.FadeOutState import FadeOutState

        if self.battle_state.final_boss:

            def on_complete() -> None:
                self.state_machine.pop()
                self.state_machine.pop()
                settings.stop_music("battle")
                settings.stop_music("world")
                settings.stop_music("town")
                settings.play_music("the-end")

                from src.states.game.TheEndState import TheEndState

                self.state_machine.push(TheEndState(self.state_machine))
                self.state_machine.push(
                    FadeOutState(self.state_machine),
                    color=(0, 0, 0),
                    time=1,
                    on_complete=lambda: None,
                )

            self.state_machine.push(
                FadeInState(self.state_machine),
                color=(0, 0, 0),
                time=3,
                on_complete=on_complete,
            )
        else:

            def on_complete() -> None:
                self.state_machine.pop()
                self.state_machine.pop()
                self.state_machine.push(
                    FadeOutState(self.state_machine),
                    color=(255, 255, 255),
                    time=1,
                    on_complete=lambda: None,
                )

            self.state_machine.push(
                FadeInState(self.state_machine),
                color=(255, 255, 255),
                time=1,
                on_complete=on_complete,
            )

    def _faint(self) -> None:
        settings.stop_music("battle")
        settings.SOUNDS["game-over"].play()

        from src.states.game.FadeInState import FadeInState

        def on_complete() -> None:
            from src.states.game.GameOverState import GameOverState
            self.state_machine.push(GameOverState(self.state_machine))

        self.state_machine.push(
            FadeInState(self.state_machine),
            color=(0, 0, 0),
            time=1,
            on_complete=on_complete,
        )

    _victory_channel = None

