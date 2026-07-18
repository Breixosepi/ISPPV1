"""
ISPPV1 2023
Study Case: Ultimate Fantasy (RPG)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class StartState: the title screen.
"""

from typing import Any

import pygame

from gale.state import BaseState

import settings


class StartState(BaseState):
    def enter(self) -> None:
        settings.play_music("intro")

    def on_input(self, input_id: str, input_data: Any) -> None:
        if input_id == "enter" and input_data.pressed:
            from src.states.game.FadeInState import FadeInState
            from src.states.game.FadeOutState import FadeOutState
            from src.states.game.SelectCharacterState import SelectCharacterState

            def on_complete() -> None:
                self.state_machine.pop()
                self.state_machine.push(
                    SelectCharacterState(self.state_machine),
                    character_index=0,
                    selected="male",
                    party={},
                )
                self.state_machine.push(
                    FadeOutState(self.state_machine),
                    color=(0, 0, 0),
                    time=0.5,
                    on_complete=lambda: None,
                )

            self.state_machine.push(
                FadeInState(self.state_machine),
                color=(0, 0, 0),
                time=1,
                on_complete=on_complete,
            )

    def render(self, surface: pygame.Surface) -> None:
        surface.blit(
            pygame.transform.scale(
                settings.TEXTURES["background"],
                (settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT),
            ),
            (0, 0),
        )

        title_font = settings.FONTS["ff"]

        shadow = title_font.render("ULTIMATE FANTASY", True, (34, 34, 34))
        shadow_rect = shadow.get_rect(
            center=(settings.VIRTUAL_WIDTH / 2 + 2, settings.VIRTUAL_HEIGHT / 2 - 20 + 2)
        )
        surface.blit(shadow, shadow_rect)

        title = title_font.render("ULTIMATE FANTASY", True, (212, 175, 55))
        title_rect = title.get_rect(
            center=(settings.VIRTUAL_WIDTH / 2, settings.VIRTUAL_HEIGHT / 2 - 20)
        )
        surface.blit(title, title_rect)

        prompt_font = settings.FONTS["medium"]
        prompt = prompt_font.render("PRESS ENTER", True, (255, 255, 255))
        prompt_rect = prompt.get_rect(
            center=(settings.VIRTUAL_WIDTH / 2, settings.VIRTUAL_HEIGHT - 40)
        )
        surface.blit(prompt, prompt_rect)
