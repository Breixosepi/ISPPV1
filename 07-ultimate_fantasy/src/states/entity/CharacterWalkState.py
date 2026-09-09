"""
ISPPV1 2026
Study Case: Ultimate Fantasy (RPG)

Author: Eugenio Montilla
eugeniorusso1411@gmail.com

This file contains the class CharacterWalkState.
"""

from src.states.entity.EntityBaseState import EntityBaseState


class CharacterWalkState(EntityBaseState):
    def enter(self) -> None:
        self.entity.change_animation(f"walk-{self.entity.direction}")
