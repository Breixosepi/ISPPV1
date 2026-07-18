"""
ISPPV1 2023
Study Case: Ultimate Fantasy (RPG)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the main program to run the game.
"""

from gale.ui.theme import set_default_theme

import settings
from src.gui.theme import DEFAULT_THEME
from src.UltimateFantasy import UltimateFantasy

if __name__ == "__main__":
    set_default_theme(DEFAULT_THEME)

    game = UltimateFantasy(
        "Ultimate Fantasy",
        settings.WINDOW_WIDTH,
        settings.WINDOW_HEIGHT,
        settings.VIRTUAL_WIDTH,
        settings.VIRTUAL_HEIGHT,
    )
    game.exec()
