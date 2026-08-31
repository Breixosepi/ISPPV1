from src.powerups.PowerUp import PowerUp
from typing import TypeVar


class PaddleCannon(PowerUp):
    def __init__(self, x: float, y: float) -> None:
        super().__init__(x, y, 3)

    def take(self,  play_state: TypeVar("PlayState")) -> None:
        play_state.cannon_controller.activate()
        self.active = False