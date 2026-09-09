

from typing import Any, Callable, Dict, List

import pygame

from gale.state import BaseState
from gale.timer import Timer

import settings
from src.gui.AlphaMenu import AlphaMenu
from src.states.game.SelectTargetState import SelectTargetState
from src.states.game.BattleMessageState import BattleMessageState

class PauseSkillsState(BaseState):
    def enter(
        self, play_state: Any, party_status_view: Any
    ) -> None:
        self.play_state = play_state
        self.party_status_view = party_status_view
        # We start in character selection mode
        self.sub_state = "select_character"
        self.party_status_view.active = False

        self.action_menu = None
        self.selected_action = None
        self.caster = None
        self.char_indices = []

        items = []
        for i, char in enumerate(self.party_status_view.characters):
            if not char.dead:
                items.append((char.name, lambda i=i: self._select_caster(i)))
                self.char_indices.append(i)
        items.append(("Back", self._exit_state))

        from src.gui.Menu import Menu
        self.character_menu = Menu(
            settings.VIRTUAL_WIDTH / 2 - 70,
            settings.VIRTUAL_HEIGHT / 2 - 48 - 30,
            140,
            len(items) * 24,
            items=items,
            font=settings.FONTS["small"]
        )

    def _select_caster(self, index: int) -> None:
        self.party_status_view.selected_index = index
        self._open_action_menu()

    def update(self, dt: float) -> None:
        if self.sub_state == "select_character":
            self.character_menu.update(dt)
            # Sync party_status_view to match the character_menu selection (unless it's "Back")
            menu_idx = self.character_menu.list_view.selected_index
            if menu_idx < len(self.char_indices):
                self.party_status_view.selected_index = self.char_indices[menu_idx]
                
        if self.action_menu is not None:
            self.action_menu.update(dt)

    def on_input(self, input_id: str, input_data: Any) -> None:
        if not input_data.pressed:
            return

        if self.sub_state == "select_character":
            if input_id == "move_up":
                self.character_menu.navigate((0, -1))
            elif input_id == "move_down":
                self.character_menu.navigate((0, 1))
            elif input_id == "enter":
                self.character_menu.confirm()

        elif self.sub_state == "select_action":
            if input_id == "move_up":
                self.action_menu.navigate((0, -1))
            elif input_id == "move_down":
                self.action_menu.navigate((0, 1))
            elif input_id == "enter":
                self.action_menu.confirm()

        elif self.sub_state == "select_target":
            if input_id == "move_up":
                self.party_status_view.change_index(-1)
            elif input_id == "move_down":
                self.party_status_view.change_index(1)
            elif input_id == "enter":
                settings.SOUNDS["blip"].stop()
                settings.SOUNDS["blip"].play()
                target = self.party_status_view.get_selected_character()
                if not target.dead:
                    self._resolve(self.selected_action, self.caster, target)

    def _open_action_menu(self) -> None:
        self.sub_state = "select_action"
        self.caster = self.party_status_view.get_selected_character()
        self.party_status_view.active = False # Deactivate view cursor
        entity = self.caster
        
        items, alphas = AlphaMenu.build_action_items(
            entity, 
            make_selector_func=lambda action: self._make_selector(action, entity),
            disabled_func=lambda: None
        )

        items.append(("Back", lambda: self._back_to_characters()))
        alphas.append(255)

        self.action_menu = AlphaMenu(
            288, settings.VIRTUAL_HEIGHT - 64 - 8, 96, 64, items=items, alphas=alphas, font=settings.FONTS["small"]
        )

    def _make_selector(self, action: Dict[str, Any], entity: Any) -> Callable[[], None]:
        return lambda: self._select_action(action, entity)

    def _select_action(self, action: Dict[str, Any], entity: Any) -> None:
        self.selected_action = action
        
        targets = list(self.play_state.world.party.characters.values())

        if action["require_target"]:
            self.sub_state = "select_target"
            self.party_status_view.active = True
            # Reset selection to 0
            self.party_status_view.selected_index = 0
            # Keep action menu visible but inactive
        else:
            alive_targets = [target for target in targets if not target.dead]
            amount = action["func"](entity, alive_targets, action.get("strength"))
            settings.SOUNDS[action["sound_effect"]].play()

            self._show_result(f"{action['name']} for {amount} HP to each target.")

    def _resolve(self, action: Dict[str, Any], entity: Any, target: Any) -> None:
        amount = action["func"](entity, target, action.get("strength"))
        settings.SOUNDS[action["sound_effect"]].play()

        self._show_result(f"{action['name']} for {amount} HP to {target.name}.")

    def _show_result(self, message: str) -> None:
        # Hide the action menu and deactivate view while showing the message
        self.action_menu = None
        self.sub_state = "select_character"
        self.party_status_view.selected_index = self.party_status_view.characters.index(self.caster)
        self.party_status_view.active = False

        from src.states.game.BattleMessageState import BattleMessageState
        self.state_machine.push(
            BattleMessageState(self.state_machine),
            battle_state=self, # mock battle state for BattleMessageState
            message=message,
            on_close=lambda: None,
        )

    # Mock property for BattleMessageState
    @property
    def enemies(self):
        return []

    def _back_to_characters(self) -> None:
        self.sub_state = "select_character"
        self.party_status_view.active = False
        self.action_menu = None

    def _exit_state(self) -> None:
        self.party_status_view.active = False
        self.state_machine.pop()

    def render(self, surface: pygame.Surface) -> None:
        self.party_status_view.render(surface)
        if self.sub_state == "select_character":
            self.character_menu.render(surface)
        if self.action_menu is not None:
            self.action_menu.render(surface)

