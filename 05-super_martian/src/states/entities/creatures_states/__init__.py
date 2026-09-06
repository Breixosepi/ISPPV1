"""
ISPPV1 2026
Study Case: Super Martian (Platformer)

Author: Eugenio Montilla
eugeniorusso1411@gmail.com

This module contains all of the creature states.
"""

from src.states.entities.creatures_states.FlyingFallState import FlyingFallState
from src.states.entities.creatures_states.FlyState import FlyState
from src.states.entities.creatures_states.SnailWalkState import SnailWalkState
__all__ = ["FlyingFallState", "FlyState", "SnailWalkState"]
