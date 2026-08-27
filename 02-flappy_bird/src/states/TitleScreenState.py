"""
ISPPV1 2023
Study Case: Flappy Bird

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the definition of the class TitleScreenState.
"""

import pygame

from gale.input_handler import InputData
from gale.state import BaseState
from gale.text import render_text

import settings
from src.World import World
from src.strategies import NormalStrategyMode
from src.strategies import HardStrategyMode


class TitleScreenState(BaseState):
    def enter(self) -> None:
        self.world = World()
        self.selected_option = 0

    def update(self, dt: float) -> None:
        self.world.update(dt)

    def render(self, surface: pygame.Surface) -> None:
        self.world.render(surface)
        render_text(
            surface,
            "Flappy Bird",
            settings.FONTS["flappy"],
            settings.VIRTUAL_WIDTH / 2,
            settings.VIRTUAL_HEIGHT / 3,
            settings.COLOR_WHITE,
            center=True,
            shadowed=True,
        )

        normal_color = settings.COLOR_WHITE if self.selected_option == 0 else (120, 120, 120)
        hard_color = settings.COLOR_WHITE if self.selected_option == 1 else (120, 120, 120)

        prefix_normal = "> " if self.selected_option == 0 else "  "
        prefix_hard = "> " if self.selected_option == 1 else "  "

        render_text(
            surface,
            f"{prefix_normal}Modo Normal",
            settings.FONTS["medium"],
            settings.VIRTUAL_WIDTH / 2,
            2 * settings.VIRTUAL_HEIGHT / 3,
            normal_color,
            center=True,
            shadowed=True,
        )

        render_text(
            surface,
            f"{prefix_hard}Modo Dificil",
            settings.FONTS["medium"],
            settings.VIRTUAL_WIDTH / 2,
            2 * settings.VIRTUAL_HEIGHT / 3 + 30, 
            hard_color,
            center=True,
            shadowed=True,
        )

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if input_id in ("up", "down") and input_data.pressed:
            self.selected_option = (self.selected_option + 1) % 2
            settings.SOUNDS["score"].play() 
            
        elif input_id == "confirm" and input_data.pressed:
            selected_mode = NormalStrategyMode() if self.selected_option == 0 else HardStrategyMode()
            self.state_machine.change("count_down", mode=selected_mode)
