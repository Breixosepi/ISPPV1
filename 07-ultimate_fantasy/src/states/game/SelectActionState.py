"""
ISPPV1 2026
Study Case: Ultimate Fantasy (RPG)

Author: Eugenio Montilla
eugeniorusso1411@gmail.com

This file contains the class SelectActionState: menu of the acting
entity's own actions.actions (whatever list its ENTITY_DEFS entry
defines) plus a trailing "Nothing" (skip turn) entry.
"""

from typing import Any, Callable, Dict, List

import pygame

from gale.state import BaseState
from gale.timer import Timer

import settings
from src.gui.Menu import Menu


class SelectActionState(BaseState):
    def enter(
        self, battle_state: Any, entity: Any, on_action_selected: Callable[[Any], None]
    ) -> None:
        self.battle_state = battle_state
        self.entity = entity
        self.on_action_selected = on_action_selected

        items = [
            (action["name"], self._make_selector(action))
            for action in self.entity.actions
        ]
        items.append(("Run", self._run))
        items.append(("Nothing", self._nothing))

        self.menu = Menu(
            288, settings.VIRTUAL_HEIGHT - 64, 96, 64, items=items, font=settings.FONTS["small"]
        )

    def _make_selector(self, action: Dict[str, Any]) -> Callable[[], None]:
        return lambda: self._select_action(action)

    def _select_action(self, action: Dict[str, Any]) -> None:
        from src.states.game.SelectTargetState import SelectTargetState

        if action["target_type"] == "enemy":
            targets: List[Any] = self.battle_state.enemies
        else:
            targets = list(self.battle_state.party.characters.values())

        self.state_machine.pop()

        if action["require_target"]:
            self.state_machine.push(
                SelectTargetState(self.state_machine),
                battle_state=self.battle_state,
                targets=targets,
                on_target_selected=lambda target: self._resolve(action, target),
            )
        else:
            alive_targets = [target for target in targets if not target.dead]
            amount = action["func"](self.entity, alive_targets, action.get("strength"))
            settings.SOUNDS[action["sound_effect"]].play()

            for target in alive_targets:
                Timer.tween(0.5, [(target.energy_bar, {"value": target.current_hp})])

            self._show_result(f"{action['name']} for {amount} HP to each target.", action)

    def _resolve(self, action: Dict[str, Any], target: Any) -> None:
        amount = action["func"](self.entity, target, action.get("strength"))
        settings.SOUNDS[action["sound_effect"]].play()
        Timer.tween(0.5, [(target.energy_bar, {"value": target.current_hp})])

        self._show_result(f"{action['name']} for {amount} HP to {target.name}.", action)

    def _show_result(self, message: str, action: Any) -> None:
        from src.states.game.BattleMessageState import BattleMessageState

        self.state_machine.push(
            BattleMessageState(self.state_machine),
            battle_state=self.battle_state,
            message=message,
            on_close=lambda: self.on_action_selected(action),
        )

    def _run(self) -> None:
        settings.SOUNDS["run"].play()
        self.state_machine.pop()
        self.on_action_selected({"name": "Run", "wait_time": 2.0})

    def _nothing(self) -> None:
        self.state_machine.pop()
        self.on_action_selected({"name": "Nothing", "wait_time": 0.4})

    def update(self, dt: float) -> None:
        for enemy in self.battle_state.enemies:
            if not enemy.dead:
                enemy.update(dt)

        self.menu.update(dt)

    def on_input(self, input_id: str, input_data: Any) -> None:
        if not input_data.pressed:
            return

        if input_id == "move_up":
            self.menu.navigate((0, -1))
        elif input_id == "move_down":
            self.menu.navigate((0, 1))
        elif input_id == "enter":
            self.menu.confirm()

    def render(self, surface: pygame.Surface) -> None:
        self.menu.render(surface)
