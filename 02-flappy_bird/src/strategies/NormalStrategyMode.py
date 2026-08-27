

from src.strategies.StrategyMode import StrategyMode
from gale.input_handler import InputData


class NormalStrategyMode(StrategyMode):
    def on_input(self, bird, input_id: str, input_data: InputData) -> None:
        if input_id == "jump" and input_data.pressed:
            bird.jump()
    def update_world(self, world, dt: float) -> None:
        world.update(dt)