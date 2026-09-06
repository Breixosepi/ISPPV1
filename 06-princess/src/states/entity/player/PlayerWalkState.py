"""
ISPPV1 2026
Study Case: The Legend of the Princess (ARPG)

Author: Eugenio Montilla
eugeniorusso1411@gmail.com

This file contains the class PlayerWalkState.
"""

from typing import TypeVar

import pygame

from gale.state import StateMachine

from src.Bow import Bow
import settings
from src.states.entity.player.PlayerActionState import PlayerActionState
from src.states.entity.movement import move_and_bump, check_doorways


class PlayerWalkState(PlayerActionState):
    def enter(self) -> None:
        self.entity.offset_y = 5
        self.entity.offset_x = 0

    def update(self, dt: float) -> None:
        if self.handle_actions():
            return

        player = self.entity
        held = player.held

        if held["move_left"]:
            player.direction = "left"
            player.change_animation("walk-left")
        elif held["move_right"]:
            player.direction = "right"
            player.change_animation("walk-right")
        elif held["move_up"]:
            player.direction = "up"
            player.change_animation("walk-up")
        elif held["move_down"]:
            player.direction = "down"
            player.change_animation("walk-down")
        else:
            player.change_state("idle")
            return

        bumped = move_and_bump(player, dt)

        if bumped:
            check_doorways(self.entity, self.dungeon, dt)

    def render(self, surface: pygame.Surface) -> None:
        anim = self.entity.current_animation
        self.entity.render_sprite(surface, anim.texture_id, anim.get_current_frame())
