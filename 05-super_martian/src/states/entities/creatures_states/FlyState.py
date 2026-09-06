"""
ISPPV1 2026
Study Case: Super Martian (Platformer)

Author: Eugenio Montilla
eugeniorusso1411@gmail.com

This file contains the class FlyState for flying creatures.
"""

from src.states.entities.BaseEntityState import BaseEntityState


class FlyState(BaseEntityState):
    has_gravity: bool = False

    def enter(self, direction: str) -> None:
        self.entity.change_animation("fly")
        # This sprite's artwork faces left by default, opposite of
        # Player's convention, so moving right is what needs the flip.
        self.entity.flipped = direction == "right"
        self.entity.vx = (
            -self.entity.fly_speed if direction == "left" else self.entity.fly_speed
        )
        self.entity.vy = 0

    def update(self, dt: float) -> None:
        if self.entity.collided_x:
            self.entity.change_state("fall")
            return

        world_width = self.entity.tilemap.pixel_width

        if (self.entity.vx < 0 and self.entity.x <= 0) or (
            self.entity.vx > 0 and self.entity.x + self.entity.width >= world_width
        ):
            self.entity.is_dead = True
