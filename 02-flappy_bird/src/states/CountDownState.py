"""
ISPPV1 2023
Study Case: Flappy Bird

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the definition of the class CountDownState.
"""

import pygame

from gale.state import Any, BaseState
from gale.text import Optional, render_text

import settings
from src.World import World
from src.strategies import NormalStrategyMode


class CountDownState(BaseState):
    def enter(self,mode: Optional[Any]= None) -> None:
        self.world = World(generate_logs=False)
        self.counter = 3
        self.timer = 0.0
        self.mode = mode if mode is not None else NormalStrategyMode()

    def update(self, dt: float) -> None:
        self.timer += dt

        if self.timer >= 1.0:
            self.timer = 0.0
            self.counter -= 1

            if self.counter == 0:
                self.state_machine.change("playing", world=self.world, mode=self.mode)
                return

        self.world.update(dt)

    def render(self, surface: pygame.Surface) -> None:
        self.world.render(surface)
        render_text(
            surface,
            str(self.counter),
            settings.FONTS["huge"],
            settings.VIRTUAL_WIDTH / 2,
            settings.VIRTUAL_HEIGHT / 2,
            settings.COLOR_WHITE,
            center=True,
            shadowed=True,
        )
