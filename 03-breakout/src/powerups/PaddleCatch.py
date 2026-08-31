from src.powerups.PowerUp import PowerUp
from typing import TypeVar

class PaddleCatch(PowerUp):
    def __init__(self, x: float, y: float) -> None:
        super().__init__(x, y, 2)

    def take(self, play_state: TypeVar("PlayState")) -> None:
        play_state.catch_controller.activate()
        self.active = False
        pass