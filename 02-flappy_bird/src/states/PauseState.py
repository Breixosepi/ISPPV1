import pygame

from gale.input_handler import InputData
from gale.state import BaseState
from gale.text import render_text

from src.Bird import Bird
from src.World import World
import settings

class PauseState(BaseState):
    def enter(self, world: World,bird:Bird,score:int) -> None:
        self.world = world
        self.bird = bird
        self.score = score

    def render(self, surface: pygame.Surface) -> None:
        self.world.render(surface)
        self.bird.render(surface)
        render_text(
            surface,
            f"Score: {self.score}",
            settings.FONTS["flappy"],
            20,
            10,
            settings.COLOR_WHITE,
            shadowed=True,
        )
        render_text(
            surface,
            "Press P to resume",
            settings.FONTS["medium"],
            settings.VIRTUAL_WIDTH / 2,
            2 * settings.VIRTUAL_HEIGHT / 3,
            settings.COLOR_WHITE,
            center=True,
            shadowed=True,
        )  

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if input_id == "pause" and input_data.pressed:
            settings.SOUNDS["score"].play()
            self.state_machine.change(
                "playing", 
                world=self.world, 
                bird=self.bird, 
                score=self.score
            )