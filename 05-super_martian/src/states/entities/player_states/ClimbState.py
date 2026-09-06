"""
ISPPV1 2026
Study Case: Super Martian (Platformer)

Author: Eugenio Montilla
eugeniorusso1411@gmail.com

This file contains the class ClimbState for player.
"""

import settings
from src.states.entities.BaseEntityState import BaseEntityState

class ClimbState(BaseEntityState):
    has_gravity: bool = False

    def enter(self) -> None:
        self.entity.vx = 0
        self.entity.vy = 0
        self.entity.change_animation("climb")

    def update(self, dt: float) -> None:
        if self.entity.jump_requested:
            self.entity.jump_requested = False
            self.entity.change_state("jump")
            return

        vy = 0
        if self.entity.move_up_requested:
            vy -= settings.CLIMB_SPEED
        if self.entity.is_looking_down:
            vy += settings.CLIMB_SPEED

        self.entity.vy = vy

        if not self.entity.is_on_ladder():
            if self.entity.on_ground:
                self.entity.change_state("idle")
            else:
                self.entity.change_state("fall")
            return

        if self.entity.on_ground and not self.entity.move_up_requested:
            if self.entity.move_direction != 0:
                self.entity.change_state("walk")
            elif not self.entity.is_looking_down:
                self.entity.change_state("idle")