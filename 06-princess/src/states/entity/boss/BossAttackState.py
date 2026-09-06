"""
ISPPV1 2026
Study Case: The Legend of the Princess (ARPG)

Author: Eugenio Montilla
eugeniorusso1411@gmail.com
BossAttackState: fires a Fireball toward the player current position.
"""
import random
from typing import TypeVar
import pygame
from gale.state import StateMachine
from src.Fireball import Fireball
from src.Projectile import Projectile
from src.states.entity.BaseEntityState import BaseEntityState


class BossAttackState(BaseEntityState):
    def __init__(self, boss: TypeVar("Entity"), state_machine: StateMachine,room: TypeVar("Room")) -> None:
        super().__init__(boss, state_machine)
        self.room = room

    def enter(self) -> None:
        self.shots_to_fire = random.randint(1, 5)
        self.shot_timer = 0.0
        self.shot_delay = 0.4
        self.shoot_fireball()

    def shoot_fireball(self) -> None:
        player = self.room.player
        bx = self.entity.x + self.entity.width  / 2
        by = self.entity.y + self.entity.height / 2
        tx = player.x + player.width  / 2
        ty = player.y + player.height / 2
        dx = tx - bx
        dy = ty - by
        if abs(dx) >= abs(dy):
            self.entity.direction = "right" if dx >= 0 else "left"
        else:
            self.entity.direction = "down" if dy >= 0 else "up"
        self.entity.change_animation(f"idle-{self.entity.direction}")
        fireball = Fireball(bx, by, tx, ty, on_hit_player=self.room.on_game_over)
        proj = Projectile(fireball, "none", speed=70, target_x=tx, target_y=ty)
        self.room.projectiles.append(proj)
        self.shots_to_fire -= 1
        self.shot_timer = 0.0

    def update(self, dt: float) -> None:
        if self.shots_to_fire > 0:
            self.shot_timer += dt
            if self.shot_timer >= self.shot_delay:
                self.shoot_fireball()
        else:
            self.entity.change_state("idle")

    def render(self, surface: pygame.Surface) -> None:
        anim = self.entity.current_animation
        self.entity.render_sprite(surface, anim.texture_id, anim.get_current_frame())
