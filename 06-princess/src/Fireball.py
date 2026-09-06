"""
ISPPV1 2026
Study Case: The Legend of the Princess (ARPG)

Author: Eugenio Montilla
eugeniorusso1411@gmail.com
Fireball projectile fired by the Boss.
Uses the 4 frames in fireball.png as a looping animation.
"""
import math
from typing import Any, Callable
import pygame
import settings

class Fireball:
    def __init__(self, x: float, y: float, target_x: float, target_y: float,
                 on_hit_player: Callable[[], None]) -> None:
        self.width  = 8
        self.height = 8
        self.x = x - self.width / 2
        self.y = y - self.height / 2
        self.dead = False
        self._on_hit_player = on_hit_player

        self._anim_timer = 0.0
        self._frame_index = 1

        dx = target_x - x
        dy = target_y - y
        dist = math.sqrt(dx * dx + dy * dy) or 1.0
        self._vx = dx / dist * settings.FIREBALL_SPEED
        self._vy = dy / dist * settings.FIREBALL_SPEED

    def get_collision_rect(self) -> pygame.Rect:
        return pygame.Rect(round(self.x), round(self.y), self.width, self.height)

    def collides(self, target: Any) -> bool:
        return self.get_collision_rect().colliderect(target.get_collision_rect())

    def update(self, dt: float) -> None:
        self._anim_timer += dt
        interval = 1.0 / settings.FIREBALL_FPS
        if self._anim_timer >= interval:
            self._anim_timer -= interval
            self._frame_index = self._frame_index % settings.FIREBALL_FRAMES + 1

    def hit_player(self) -> None:
        if not self.dead:
            self.dead = True
            self._on_hit_player()

    def render(self, surface: pygame.Surface, offset_x: float = 0, offset_y: float = 0) -> None:
        frame_rect = settings.frame("fireball", self._frame_index)
        sprite = settings.TEXTURES["fireball"].subsurface(frame_rect)
        if self._vx < 0:
            sprite = pygame.transform.flip(sprite, True, False)
        
        surface.blit(
            sprite,
            (self.x + offset_x - 4, self.y + offset_y - 4)
        )
