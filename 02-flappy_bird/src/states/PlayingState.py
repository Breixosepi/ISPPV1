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
from src.strategies import HardStrategyMode


class PlayingState(BaseState):
    def enter(self, world: Optional[World] = None, bird:Optional[Bird] = None,score :int = 0, mode: Optional[Any] = None) -> None:
        self.mode = mode if mode is not None else NormalStrategyMode()
        self.world = world if world is not None else World()

        if bird is not None:
            self.bird = bird
        else:
            is_hard = isinstance(self.mode, HardStrategyMode)
            self.world.reset(generate_logs = not is_hard, generate_booster = is_hard)
            self.bird = Bird(
                settings.VIRTUAL_WIDTH / 2 - settings.BIRD_WIDTH / 2,
                settings.VIRTUAL_HEIGHT / 2 - settings.BIRD_HEIGHT / 2,
                settings.BIRD_WIDTH,
                settings.BIRD_HEIGHT,
            )
        self.score = score
        self.was_boosted = False
        self.mode = mode if mode is not None else NormalStrategyMode()

    def update(self, dt: float) -> None:
        self.bird.update(dt)
        self.mode.update_world(self.world, dt)

        if self.world.check_booster(self.bird.get_rect()):
            self.bird.activate_boost(6.0)
            settings.SOUNDS["booster_effect"].play()
            pygame.mixer.music.pause()

        current_boost_state = getattr(self.bird, "is_boosted", False)
        if self.was_boosted and not current_boost_state:
            pygame.mixer.music.unpause()
        self.was_boosted = current_boost_state

        if self.world.collides(self.bird.get_rect(),ignore=self.bird.is_boosted):
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