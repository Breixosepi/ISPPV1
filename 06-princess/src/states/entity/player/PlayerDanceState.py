import pygame
from typing import TypeVar
from gale.state import StateMachine
from src.states.entity.BaseEntityState import BaseEntityState

class PlayerDanceState(BaseEntityState):
    def __init__(
        self,
        player: TypeVar("Player"),
        state_machine: StateMachine,
        dungeon: TypeVar("Dungeon"),
    ) -> None:
        super().__init__(player, state_machine)
        self.dungeon = dungeon

    def enter(self) -> None:
        self.entity.offset_y = 5
        self.entity.offset_x = 0
        self.entity.change_animation("dance")
        self.entity.current_animation.reset()

    def update(self, dt: float) -> None:
        if not self.entity.dance_held:
            self.entity.change_state("idle")
            return

    def render(self, surface: pygame.Surface) -> None:
        anim = self.entity.current_animation
        self.entity.render_sprite(surface, anim.texture_id, anim.get_current_frame())
