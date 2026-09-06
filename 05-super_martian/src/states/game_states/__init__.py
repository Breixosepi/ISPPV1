"""
ISPPV1 2026
Study Case: Super Martian (Platformer)

Author: Eugenio Montilla
eugeniorusso1411@gmail.com

This module contains all of the game states.
"""

from src.states.game_states.GameOverState import GameOverState
from src.states.game_states.PauseState import PauseState
from src.states.game_states.PlayState import PlayState
from src.states.game_states.StartState import StartState
__all__ = ["GameOverState", "PauseState", "PlayState", "StartState"]
