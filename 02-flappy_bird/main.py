"""
ISPPV1 2023
Study Case: Flappy Bird

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the main program to run the game.
"""

import settings
from src.FlappyBird import FlappyBird

if __name__ == "__main__":
    game = FlappyBird(
        "Flappy Bird",
        settings.WINDOW_WIDTH,
        settings.WINDOW_HEIGHT,
        settings.VIRTUAL_WIDTH,
        settings.VIRTUAL_HEIGHT,
    )
    game.exec()
