"""
ISPPV1 2026
Study Case: Ultimate Fantasy (RPG)

Author: Eugenio Montilla
eugeniorusso1411@gmail.com

This file contains the main program to run the game.
"""

from gale.ui.theme import set_default_theme

from src.gui.theme import DEFAULT_THEME
from src.UltimateFantasy import UltimateFantasy

if __name__ == "__main__":
    set_default_theme(DEFAULT_THEME)
    game = UltimateFantasy()
    game.exec()
