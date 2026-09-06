"""
ISPPV1 2026
Study Case: The Legend of the Princess (ARPG)

Author: Eugenio Montilla
eugeniorusso1411@gmail.com
BossChaseState: Boss walks towards the player for a set duration, then attacks.
"""
import random
from typing import TypeVar
import pygame
from src import commands
from src.states.entity.BaseEntityState import BaseEntityState
from src.states.entity.movement import move_and_bump

_MOVE_COMMANDS = {
    "left": commands.MOVE_LEFT,
    "right": commands.MOVE_RIGHT,
    "up": commands.MOVE_UP,
    "down": commands.MOVE_DOWN,
}
_STOP_COMMANDS = (
    commands.STOP_MOVE_LEFT,
    commands.STOP_MOVE_RIGHT,
    commands.STOP_MOVE_UP,
    commands.STOP_MOVE_DOWN,
)

class BossChaseState(BaseEntityState):
    def __init__(self, boss: TypeVar("Entity"), state_machine: TypeVar("StateMachine"), room: TypeVar("Room")) -> None:
        super().__init__(boss, state_machine)
        self.room = room

    def enter(self) -> None:
        self.chase_duration = random.uniform(1.0, 2.0)
        self.chase_timer = 0.0
        self._pick_direction_towards_player()

    def _pick_direction_towards_player(self) -> None:
        for stop in _STOP_COMMANDS:
            stop.execute(self.entity)
            
        player = self.room.player
        dx = (player.x + player.width / 2) - (self.entity.x + self.entity.width / 2)
        dy = (player.y + player.height / 2) - (self.entity.y + self.entity.height / 2)
        
        if abs(dx) > abs(dy):
            direction = "right" if dx > 0 else "left"
        else:
            direction = "down" if dy > 0 else "up"
            
        _MOVE_COMMANDS[direction].execute(self.entity)
        self.entity.change_animation(f"walk-{direction}")
        self.current_direction = direction

    def update(self, dt: float) -> None:
        bumped = move_and_bump(self.entity, dt)
        if bumped:
            self._pick_direction_towards_player()

    def process_ai(self, room: TypeVar("Room"), dt: float) -> None:
        self.chase_timer += dt
        
        if self.chase_timer >= self.chase_duration:
            for stop in _STOP_COMMANDS:
                stop.execute(self.entity)
            self.entity.change_state("attack")

    def render(self, surface: pygame.Surface) -> None:
        anim = self.entity.current_animation
        self.entity.render_sprite(surface, anim.texture_id, anim.get_current_frame())

