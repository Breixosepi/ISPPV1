"""
ISPPV1 2026
Study Case: Super Martian (Platformer)

Author: Eugenio Montilla
eugeniorusso1411@gmail.com

This file contains the base class BaseEntityState.
"""

from typing import TypeVar

from gale.state import BaseState, StateMachine


class BaseEntityState(BaseState):
    has_gravity: bool = True

    def __init__(
        self, entity: TypeVar("GameEntity"), state_machine: StateMachine
    ) -> None:
        super().__init__(state_machine)
        self.entity = entity
