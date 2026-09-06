"""
ISPPV1 2026
Study Case: The Legend of the Princess (ARPG)

Author: Eugenio Montilla
eugeniorusso1411@gmail.com
BossIdleState: boss waits, then transitions to BossAttackState.
"""
import random
from typing import TypeVar
import pygame
from gale.state import StateMachine
from src.states.entity.BaseEntityState import BaseEntityState

class BossIdleState(BaseEntityState):
    def __init__(self, boss: TypeVar("Entity"), state_machine: StateMachine,room: TypeVar("Room")) -> None:
        super().__init__(boss, state_machine)
        self.room = room

    def enter(self) -> None:
        self.entity.change_animation(f"idle-{self.entity.direction}")
        self.wait_duration = random.uniform(2.0, 4.0)
        self.wait_timer = 0.0

    def process_ai(self, room: TypeVar("Room"), dt: float) -> None:
        self.wait_timer += dt
        if self.wait_timer >= self.wait_duration:
            self.entity.change_state("walk")

    def render(self, surface: pygame.Surface) -> None:
        anim = self.entity.current_animation
        self.entity.render_sprite(surface, anim.texture_id, anim.get_current_frame())
