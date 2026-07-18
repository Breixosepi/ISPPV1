"""
ISPPV1 2023
Study Case: Ultimate Fantasy (RPG)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class PlayState: hosts the World (overworld
regions + party) for as long as the player is out of battle.
"""

from typing import Any, Dict

import pygame

from gale.state import BaseState

from src.world.World import World


class PlayState(BaseState):
    def enter(self, party_genders: Dict[int, str]) -> None:
        self.world = World(self.state_machine, party_genders)

    def update(self, dt: float) -> None:
        self.world.update(dt)

    def on_input(self, input_id: str, input_data: Any) -> None:
        self.world.on_input(input_id, input_data)

    def render(self, surface: pygame.Surface) -> None:
        self.world.render(surface)
