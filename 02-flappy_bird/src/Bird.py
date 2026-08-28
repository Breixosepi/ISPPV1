"""
ISPPV1 2023
Study Case: Flappy Bird

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the definition of the class Bird.
"""

import pygame

import settings


class Bird:
    def __init__(self, x: float, y: float, width: float, height: float) -> None:
        self.x: float = x
        self.y: float = y
        self.width: float = width
        self.height: float = height
        self.vy: float = 0.0
        self.vx: float = 0.0
        self.jumping: bool = False
        self.is_boosted: bool = False
        self.boost_duration: float = 0.0

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(round(self.x), round(self.y), self.width, self.height)

    def jump(self) -> None:
        self.jumping = True

    def activate_boost(self, duration: float) -> None:
        self.is_boosted = True
        self.boost_duration = duration

    def update(self, dt: float) -> None:

        if self.is_boosted:
            self.boost_duration -= dt
            if self.boost_duration <= 0:
                self.is_boosted = False

        self.vy += settings.GRAVITY * dt

        if self.jumping:
            settings.SOUNDS["jump"].play()
            self.vy = -settings.JUMP_TAKEOFF_SPEED
            self.jumping = False

        self.y += self.vy * dt

        self.x += self.vx * dt

        if self.x < 0:
            self.x = 0
        elif self.x > settings.VIRTUAL_WIDTH - self.width:
            self.x = settings.VIRTUAL_WIDTH - self.width

    def render(self, surface: pygame.Surface) -> None:
        if self.is_boosted:
            ghost_img = settings.TEXTURES["bird"].copy()
            ghost_img.set_alpha(128)
            surface.blit(ghost_img, self.get_rect())
        else:
            surface.blit(settings.TEXTURES["bird"], self.get_rect())
