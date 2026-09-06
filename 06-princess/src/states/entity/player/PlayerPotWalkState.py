"""
ISPPV1 2026
Study Case: The Legend of the Princess (ARPG)

Author: Eugenio Montilla
eugeniorusso1411@gmail.com

This file contains the class PlayerPotWalkState.
"""

from typing import Any, TypeVar

import pygame

from gale.state import StateMachine

import settings
from src.Projectile import Projectile
from src.states.entity.BaseEntityState import BaseEntityState
from src.states.entity.movement import move_and_bump, check_doorways


class PlayerPotWalkState(BaseEntityState):
    def __init__(
        self,
        player: TypeVar("Player"),
        state_machine: StateMachine,
        dungeon: TypeVar("Dungeon"),
    ) -> None:
        super().__init__(player, state_machine)
        self.dungeon = dungeon

        self.entity.offset_y = 5
        self.entity.offset_x = 0

    def enter(self, pot: Any) -> None:
        self.pot = pot

    def update(self, dt: float) -> None:
        player = self.entity

        player.sword_requested = False

        if player.interact_requested:
            player.interact_requested = False
            self.dungeon.current_room.projectiles.append(
                Projectile(self.pot, player.direction)
            )
            player.change_state("idle")
            return

        held = player.held

        if held["move_left"]:
            player.direction = "left"
            player.change_animation("pot-walk-left")
        elif held["move_right"]:
            player.direction = "right"
            player.change_animation("pot-walk-right")
        elif held["move_up"]:
            player.direction = "up"
            player.change_animation("pot-walk-up")
        elif held["move_down"]:
            player.direction = "down"
            player.change_animation("pot-walk-down")
        else:
            player.change_state("pot-idle", pot=self.pot)
            return

        bumped = move_and_bump(player, dt)

        if bumped:
            check_doorways(self.entity, self.dungeon, dt)

        self.pot.x = player.x
        self.pot.y = player.y - self.pot.height / 2

    def render(self, surface: pygame.Surface) -> None:
        anim = self.entity.current_animation
        self.entity.render_sprite(surface, anim.texture_id, anim.get_current_frame())
        self.pot.render(surface)
