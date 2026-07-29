"""
ISPPV1 2023
Study Case: Match-3

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the main program to run the game.
"""

from src.Match3 import Match3

if __name__ == "__main__":
    # Match3 takes every gale.game.Game argument (title, window size,
    # ...) straight from settings.py / gale.conf.global_settings, so
    # there's no need to pass any of them here -- see settings.py.
    match3 = Match3()
    match3.exec()
