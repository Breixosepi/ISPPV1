from src.powerups.PowerUp import PowerUp
from typing import TypeVar


class Fireball(PowerUp):
    def __init__(self, x: float, y: float) -> None:
        super().__init__(x, y, 0)

    def take(self, play_state: TypeVar("PlayState")) -> None:
        play_state.fireball_controller.activate()
        self.active = False