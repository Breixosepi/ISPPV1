    

from abc import ABC, abstractmethod
from gale.input_handler import InputData


class StrategyMode(ABC):

    @abstractmethod
    def on_input(self, bird, input_id: str, input_data: InputData) -> None:
        pass

    @abstractmethod
    def update_world(self, world, dt: float) -> None:
        pass