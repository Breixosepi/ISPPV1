import math
import random
from typing import List

import pygame

import settings


class FireballController:
    def __init__(self) -> None:
        self.active = False
        self.timer = 0.0

        texture = settings.TEXTURES["fireball"]
        rect_frames_by_color = settings.FRAMES["fireballs"]

        self.frames_by_color: List[List[pygame.Surface]] = [
            [texture.subsurface(rect) for rect in color_row]
            for color_row in rect_frames_by_color
        ]

        self.current_color_idx = 0
        self.frame_index = 0
        self.anim_timer = 0.0

    def activate(self, duration: float = 5.0) -> None:
        self.active = True
        self.timer = duration
        self.current_color_idx = random.randint(0, len(self.frames_by_color) - 1)

    def is_active(self) -> bool:
        return self.active

    def update(self, dt: float, play_state=None) -> None:
        if not self.active:
            return

        self.timer -= dt
        if self.timer <= 0:
            self.active = False
            return

        self.anim_timer += dt
        if self.anim_timer >= 0.08:
            self.anim_timer = 0.0
            frames_count = len(self.frames_by_color[self.current_color_idx])
            self.frame_index = (self.frame_index + 1) % frames_count

    def render(self, surface: pygame.Surface, balls: list) -> None:
        if not self.active:
            return

        current_raw = self.frames_by_color[self.current_color_idx][self.frame_index]

        for ball in balls:
            if not getattr(ball, "active", True):
                continue

            dx = ball.vx
            dy = ball.vy

            angle = math.degrees(math.atan2(-dy, dx))
            rotated_sprite = pygame.transform.rotate(current_raw, angle)
            rot_rect = rotated_sprite.get_rect()

            ball_rect = ball.get_collision_rect()
            rot_rect.center = ball_rect.center

            surface.blit(rotated_sprite, rot_rect)