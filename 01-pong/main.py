"""
ISPPV1 2023
Study Case: Pong

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the main program to run the pong game.
"""

from src.Pong import Pong

if __name__ == "__main__":
    # Pong takes every gale.game.Game argument (title, window size,
    # ...) straight from settings.py / gale.conf.global_settings, so
    # there's no need to pass any of them here -- see settings.py.
    game = Pong()
    game.exec()
