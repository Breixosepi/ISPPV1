"""
ISPPV1 2026
Study Case: Super Martian (Platformer)

Author: Eugenio Montilla
eugeniorusso1411@gmail.com

This file contains helper functions to render the game HUD.
"""

import pygame
from gale.text import render_text

import settings


def render_hud(surface: pygame.Surface, score: int, time: int) -> None:
    render_text(
        surface,
        f"Score: {score}",
        settings.FONTS["small"],
        5,
        5,
        (255, 255, 255),
        shadowed=True,
    )

    render_text(
        surface,
        f"Time: {time}",
        settings.FONTS["small"],
        settings.VIRTUAL_WIDTH - 60,
        5,
        (255, 255, 255),
        shadowed=True,
    )
