"""
ISPPV1 2023
Study Case: Throw a Bird

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the main program to run the game.
"""

import settings
from src.ThrowABird import ThrowABird

if __name__ == "__main__":
    game = ThrowABird(
        "Throw a Bird",
        settings.WINDOW_WIDTH,
        settings.WINDOW_HEIGHT,
        settings.VIRTUAL_WIDTH,
        settings.VIRTUAL_HEIGHT,
    )
    game.exec()
