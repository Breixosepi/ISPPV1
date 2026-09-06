"""
ISPPV1 2026
Study Case: The Legend of the Princess (ARPG)

Author: Eugenio Montilla
eugeniorusso1411@gmail.com

This file contains the class Projectile.
"""

import math
from typing import Any
import pygame
import settings

_SPEED = 150
_MAX_TILES = 4

class Projectile:
    def __init__(self, obj: Any, direction: str, speed: float = _SPEED, target_x: float = None, target_y: float = None) -> None:
        self.obj = obj
        self.direction = direction
        self.distance = 0.0
        self.dead = False
        self.speed = speed
        self.vx = 0.0
        self.vy = 0.0
        
        if target_x is not None and target_y is not None:
            dx = target_x - obj.x
            dy = target_y - obj.y
            dist = math.hypot(dx, dy)
            if dist != 0:
                self.vx = (dx / dist) * speed
                self.vy = (dy / dist) * speed

    def get_collision_rect(self) -> pygame.Rect:
        return self.obj.get_collision_rect()

    def update(self, dt: float) -> None:
        if self.dead:
            return

        d = self.speed * dt

        if self.vx != 0 or self.vy != 0:
            self.obj.x += self.vx * dt
            self.obj.y += self.vy * dt
            
            out = (
                self.obj.x + self.obj.width < settings.MAP_RENDER_OFFSET_X
                or self.obj.x > settings.MAP_RENDER_OFFSET_X + settings.MAP_WIDTH * settings.TILE_SIZE
                or self.obj.y + self.obj.height < settings.MAP_RENDER_OFFSET_Y
                or self.obj.y > settings.MAP_RENDER_OFFSET_Y + settings.MAP_HEIGHT * settings.TILE_SIZE
            )
            if out:
                self.dead = True
        else:
            if self.direction == "up":
                self.obj.y -= d
                limit = settings.MAP_RENDER_OFFSET_Y + settings.TILE_SIZE - self.obj.height / 2
                if self.obj.y <= limit:
                    self.obj.y = limit
                    self.dead = True
            elif self.direction == "down":
                self.obj.y += d
                bottom_edge = (
                    settings.MAP_HEIGHT * settings.TILE_SIZE
                    + settings.MAP_RENDER_OFFSET_Y
                    - settings.TILE_SIZE
                )
                if self.obj.y + self.obj.height >= bottom_edge:
                    self.obj.y = bottom_edge - self.obj.height
                    self.dead = True
            elif self.direction == "left":
                self.obj.x -= d
                limit = settings.MAP_RENDER_OFFSET_X + settings.TILE_SIZE
                if self.obj.x <= limit:
                    self.obj.x = limit
                    self.dead = True
            elif self.direction == "right":
                self.obj.x += d
                limit = settings.VIRTUAL_WIDTH - settings.TILE_SIZE * 2
                if self.obj.x + self.obj.width >= limit:
                    self.obj.x = limit - self.obj.width
                    self.dead = True

        if self.dead:
            if self.vx == 0 and self.vy == 0 and not getattr(self.obj, "is_arrow", False):
                settings.SOUNDS["pot-wall"].play()
            return

        self.distance += d
        
        if getattr(self.obj, "is_arrow", False) or self.vx != 0 or self.vy != 0:
            pass
        elif self.distance > _MAX_TILES * settings.TILE_SIZE:
            self.dead = True

    def render(
        self, surface: pygame.Surface, offset_x: float = 0, offset_y: float = 0
    ) -> None:
        if getattr(self.obj, "is_arrow", False) or getattr(self.obj, "type", None) == "arrow":
            angles = {"right": 0, "up": 90, "left": 180, "down": 270}
            angle = angles.get(self.direction, 0)
            frame_rect = settings.frame("arrow", 1)
            base = settings.TEXTURES["arrow"].subsurface(frame_rect)
            rotated = pygame.transform.rotate(base, angle)
            rx = self.obj.x + offset_x + (self.obj.width - rotated.get_width()) / 2
            ry = self.obj.y + offset_y + (self.obj.height - rotated.get_height()) / 2
            surface.blit(rotated, (rx, ry))
        else:
            self.obj.render(surface, offset_x, offset_y)

    def collides(self, target: Any) -> bool:
        return self.get_collision_rect().colliderect(target.get_collision_rect())
