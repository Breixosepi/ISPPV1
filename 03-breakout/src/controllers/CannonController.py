from typing import List
import pygame
import settings
from src.Paddle import Paddle
from src.Laser import Laser


class CannonController:
    def __init__(self, paddle: Paddle) -> None:
        self.paddle = paddle
        self.active = False
        self.timer = 0.0
        self.projectiles: List[Laser] = []
        texture = settings.TEXTURES["cannon"]
        rect_frames = settings.FRAMES["cannons"]
        self.frames: List[pygame.Surface] = []

        for rect in rect_frames:
            raw_subsurface = texture.subsurface(rect)
            rotated = pygame.transform.rotate(raw_subsurface, 90)
            scaled = pygame.transform.scale(rotated, (12, 14))
            self.frames.append(scaled)

        self.frame_index = 0
        self.animating = False
        self.anim_timer = 0.0

    def activate(self, duration: float = 8.0) -> None:
        self.active = True
        self.timer = duration

    def fire(self) -> None:
        if not self.active or len(self.projectiles) > 0:
            return

        cannon_w = self.frames[0].get_width()
        left_x = self.paddle.x + 1 + (cannon_w // 2) - 1
        right_x = (self.paddle.x + self.paddle.width - cannon_w - 1) + (cannon_w // 2) - 1
        spawn_y = self.paddle.y - 10

        self.projectiles.append(Laser(left_x, spawn_y))
        self.projectiles.append(Laser(right_x, spawn_y))

        self.animating = True
        self.frame_index = 0
        self.anim_timer = 0.0

        if "paddle_hit" in settings.SOUNDS:
            settings.SOUNDS["paddle_hit"].stop()
            settings.SOUNDS["paddle_hit"].play()

    def update(self, dt: float, play_state) -> None:
        if self.active:
            self.timer -= dt
            if self.timer <= 0:
                self.active = False

        if self.animating:
            self.anim_timer += dt
            if self.anim_timer >= 0.04:
                self.anim_timer = 0.0
                self.frame_index += 1
                if self.frame_index >= len(self.frames):
                    self.frame_index = 0
                    self.animating = False

        for projectile in self.projectiles:
            projectile.update(dt)
            projectile_rect = projectile.get_collision_rect()

            for brick in play_state.brickset.bricks.values():
                if getattr(brick, "broken", False):
                    continue

                if projectile_rect.colliderect(brick.get_collision_rect()):
                    brick.hit()
                    brick.active = False
                    play_state.score += brick.score()
                    projectile.active = False
                    break

            if not projectile.active:
                break

        self.projectiles = [p for p in self.projectiles if p.active]

    def render(self, surface: pygame.Surface) -> None:
        for projectile in self.projectiles:
            projectile.render(surface)

        if self.active:
            current_sprite = self.frames[self.frame_index]
            cannon_w = current_sprite.get_width()
            y_pos = int(self.paddle.y - 10)

            left_x = int(self.paddle.x + 1)
            surface.blit(current_sprite, (left_x, y_pos))

            right_x = int(self.paddle.x + self.paddle.width - cannon_w - 1)
            surface.blit(current_sprite, (right_x, y_pos))