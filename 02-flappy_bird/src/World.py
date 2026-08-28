"""
ISPPV1 2023
Study Case: Flappy Bird

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the definition of the class World: the scrolling
background/ground, and the log pairs the bird must fly through.
"""

import random
from typing import List

import pygame

from gale.factory import Factory

import settings
from src.LogPair import LogPair
from src.Booster import Booster


class World:
    def __init__(self, generate_logs: bool = False, generate_boosters: bool = False) -> None:
        self.generate_logs: bool = generate_logs
        self.generate_boosters: bool = generate_boosters
        self.background_x: float = 0.0
        self.ground_x: float = 0.0
        self.logs: List[LogPair] = []
        self.logs_spawn_timer: float = 0.0
        self.last_log_y: float = -settings.LOG_HEIGHT + random.randint(0, 80) + 20
        self.log_pair_factory: Factory = Factory(LogPair)
        self.boosters: List[Booster] = []
        self.boosters_spawn_timer: float = 0.0
        self.boosters_factory: Factory = Factory(Booster)
        self.next_booster_time: float = random.uniform(8.0, 16.0) 

    def reset(self, generate_logs: bool, generate_booster: bool) -> None:
        self.generate_logs = generate_logs
        self.generate_boosters = generate_booster

    def collides(self, rect: pygame.Rect, ignore: bool =False) -> bool:

        if rect.bottom >= settings.VIRTUAL_HEIGHT:
            return True

        if ignore:
            return False
        
        return any(log_pair.collides(rect) for log_pair in self.logs)

    def check_booster(self, rect: pygame.Rect) -> bool:
        for booster in self.boosters:
            if booster.activate and booster.get_rect().colliderect(rect):
                booster.activate = False
                return True
        return False

    def update_scored(self, rect: pygame.Rect) -> bool:
        return any(log_pair.update_scored(rect) for log_pair in self.logs)

    def update(self, dt: float) -> None:
        if self.generate_logs:
            self.logs_spawn_timer += dt

            if self.logs_spawn_timer >= settings.TIME_TO_SPAWN_LOGS:
                self.logs_spawn_timer = 0.0
                y = max(
                    -settings.LOG_HEIGHT + 10,
                    min(
                        self.last_log_y + random.randint(-20, 20),
                        settings.VIRTUAL_HEIGHT + 90 - settings.LOG_HEIGHT,
                    ),
                )
                self.last_log_y = y
                self.logs.append(self.log_pair_factory.create(settings.VIRTUAL_WIDTH, y))
        if self.generate_boosters:
            self.boosters_spawn_timer += dt

            if self.boosters_spawn_timer >= self.next_booster_time:
                any_log_active = any(log.x >= settings.VIRTUAL_WIDTH - 100 for log in self.logs)
                if not any_log_active:
                    self.boosters_spawn_timer = 0.0
                    self.next_booster_time = random.uniform(8, 14)
                    b_y = random.randint(50, settings.VIRTUAL_HEIGHT - 50 - settings.BOOSTER_HEIGHT)
                    self.boosters.append(self.boosters_factory.create(settings.VIRTUAL_WIDTH, b_y))
                else:
                    self.boosters_spawn_timer -= 0.5


        self.background_x += -settings.BACK_SCROLL_SPEED * dt

        if self.background_x <= -settings.BACKGROUND_LOOPING_POINT:
            self.background_x = 0

        self.ground_x += -settings.MAIN_SCROLL_SPEED * dt

        if self.ground_x <= -settings.VIRTUAL_WIDTH:
            self.ground_x = 0

        for booster in self.boosters:
            booster.update(dt)

        self.boosters = [booster for booster in self.boosters if not booster.is_out_of_game() and booster.activate]

        for log_pair in self.logs:
            log_pair.update(dt)

        self.logs = [log_pair for log_pair in self.logs if not log_pair.is_out_of_game()]

    def render(self, surface: pygame.Surface) -> None:
        surface.blit(settings.TEXTURES["background"], (round(self.background_x), 0))

        for log_pair in self.logs:
            log_pair.render(surface)

        for booster in self.boosters:
            booster.render(surface)

        surface.blit(
            settings.TEXTURES["ground"],
            (round(self.ground_x), settings.VIRTUAL_HEIGHT - settings.GROUND_HEIGHT),
        )
