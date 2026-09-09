"""
ISPPV1 2026
Study Case: Ultimate Fantasy (RPG)

Author: Eugenio Montilla
eugeniorusso1411@gmail.com

This file contains the class CharacterIdleState.
"""

from src.states.entity.EntityBaseState import EntityBaseState


class CharacterIdleState(EntityBaseState):
    def enter(self) -> None:
        self.entity.change_animation(f"idle-{self.entity.direction}")
