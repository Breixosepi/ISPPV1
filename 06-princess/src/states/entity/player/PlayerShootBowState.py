"""
ISPPV1 2026
Study Case: The Legend of the Princess (ARPG)

Author: Eugenio Montilla
eugeniorusso1411@gmail.com

This file contains the class PlayerShootBowState.
"""

from typing import TypeVar

import pygame

from gale.state import StateMachine

import settings
from src.states.entity.BaseEntityState import BaseEntityState
from src.Bow import Bow


class PlayerShootBowState(BaseEntityState):
    def __init__(
        self,
        player: TypeVar("Player"),
        state_machine: StateMachine,
        dungeon: TypeVar("Dungeon"),
    ) -> None:
        super().__init__(player, state_machine)
        self.dungeon = dungeon
        self.fired = False

    def enter(self) -> None:
        self.entity.offset_x = 8
        self.entity.offset_y = 5
        self.entity.change_animation(f"bow-{self.entity.direction}")
        self.entity.current_animation.reset()
        self.fired = False

    def update(self, dt: float) -> None:
        if self.entity.current_animation.current_frame_index == 2 and not self.fired:
            self.fired = True
            arrow = Bow.fire(self.entity)
            self.dungeon.current_room.projectiles.append(arrow)
            settings.SOUNDS["bow"].play()

        if self.entity.current_animation.times_played > 0:
            self.entity.current_animation.times_played = 0
            self.entity.change_state("idle")

    def render(self, surface: pygame.Surface) -> None:
        anim = self.entity.current_animation
        self.entity.render_sprite(surface, anim.texture_id, anim.get_current_frame())
