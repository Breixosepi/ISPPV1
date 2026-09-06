"""
ISPPV1 2026
Study Case: The Legend of the Princess (ARPG)

Author: Eugenio Montilla
eugeniorusso1411@gmail.com
PlayerActionState: Base class for PlayerIdleState and PlayerWalkState to handle common inputs.
"""
from typing import TypeVar
import pygame
from gale.state import StateMachine
from src.states.entity.BaseEntityState import BaseEntityState

class PlayerActionState(BaseEntityState):
    def __init__(
        self,
        player: TypeVar("Player"),
        state_machine: StateMachine,
        dungeon: TypeVar("Dungeon"),
    ) -> None:
        super().__init__(player, state_machine)
        self.dungeon = dungeon

    def handle_actions(self) -> bool:
        """Handles sword, bow, dance, and interactions. Returns True if state changed."""
        player = self.entity

        if player.sword_requested:
            player.sword_requested = False
            player.change_state("swing-sword")
            return True

        if player.bow_requested:
            player.bow_requested = False
            if player.has_bow:
                player.change_state("shoot-bow")
                return True

        if player.dance_held:
            player.change_state("dance")
            return True

        if player.interact_requested:
            player.interact_requested = False

            self.dungeon.current_room.interact_with_chest(player)
            if player.state_machine.current is not self:
                return True

            self.dungeon.current_room.take_adjacent_pot(player)
            if player.state_machine.current is not self:
                return True

        return False

