"""
ISPPV1 2023
Study Case: Hello World

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the main program to run the game.
"""

import settings
from src.HelloWorld import HelloWorld

if __name__ == "__main__":
    game = HelloWorld(
        "Hello World",
        settings.WINDOW_WIDTH,
        settings.WINDOW_HEIGHT,
        settings.VIRTUAL_WIDTH,
        settings.VIRTUAL_HEIGHT,
    )
    game.exec()
