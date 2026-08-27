"""
ISPPV1 2023
Study Case: Flappy Bird

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the definition of the class PlayingState.
"""

from typing import Optional

import pygame

from gale.input_handler import InputData
from gale.state import Any, BaseState
from gale.text import render_text

import settings
from src.Bird import Bird
from src.World import World

from src.strategies import NormalStrategyMode


class PlayingState(BaseState):
    def enter(self, world: Optional[World] = None, bird:Optional[Bird] = None,score :int = 0, mode: Optional[Any] = None) -> None:
        self.world = world if world is not None else World()

        if bird is not None:
            self.bird = bird
        else:
            self.world.reset(True)
            self.bird = Bird(
                settings.VIRTUAL_WIDTH / 2 - settings.BIRD_WIDTH / 2,
                settings.VIRTUAL_HEIGHT / 2 - settings.BIRD_HEIGHT / 2,
                settings.BIRD_WIDTH,
                settings.BIRD_HEIGHT,
            )
        self.score = score
        self.mode = mode if mode is not None else NormalStrategyMode()

    def update(self, dt: float) -> None:
        self.bird.update(dt)
        self.mode.update_world(self.world, dt)

        if self.world.collides(self.bird.get_rect()):
            settings.SOUNDS["explosion"].play()
            settings.SOUNDS["hurt"].play()
            self.state_machine.change("title")
            return

        if self.world.update_scored(self.bird.get_rect()):
            self.score += 1
            settings.SOUNDS["score"].play()

    def render(self, surface: pygame.Surface) -> None:
        self.world.render(surface)
        self.bird.render(surface)
        render_text(
            surface,
            f"Score: {self.score}",
            settings.FONTS["flappy"],
            20,
            10,
            settings.COLOR_WHITE,
            shadowed=True,
        )

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if input_id == "pause" and input_data.pressed:
            settings.SOUNDS["score"].play()
            self.state_machine.change(
                "pause", 
                world=self.world, 
                bird=self.bird, 
                score=self.score,
                mode =self.mode
            )
            return
        self.mode.on_input(self.bird, input_id, input_data)