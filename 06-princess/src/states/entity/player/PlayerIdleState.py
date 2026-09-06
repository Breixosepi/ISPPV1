"""
ISPPV1 2026
Study Case: The Legend of the Princess (ARPG)

Author: Eugenio Montilla
eugeniorusso1411@gmail.com

This file contains the class PlayerIdleState.
"""

from typing import TypeVar

import pygame

from gale.state import StateMachine

from src.Bow import Bow
from src.states.entity.player.PlayerActionState import PlayerActionState
import settings


class PlayerIdleState(PlayerActionState):
    def enter(self) -> None:
        self.entity.offset_y = 5
        self.entity.offset_x = 0
        self.entity.change_animation(f"idle-{self.entity.direction}")

    def update(self, dt: float) -> None:
        if self.handle_actions():
            return

        player = self.entity
        held = player.held

        if held["move_left"] or held["move_right"] or held["move_up"] or held["move_down"]:
            player.change_state("walk")

    def render(self, surface: pygame.Surface) -> None:
        anim = self.entity.current_animation
        self.entity.render_sprite(surface, anim.texture_id, anim.get_current_frame())
