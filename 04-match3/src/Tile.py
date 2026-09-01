"""
ISPPV1 2023
Study Case: Match-3

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class Tile.
"""
from typing import Optional, Any
import pygame

import settings


class Tile:
    def __init__(self, i: int, j: int, color: int, variety: int, power_up : Optional[Any] = None) -> None:
        self.i = i
        self.j = j
        self.x = self.j * settings.TILE_SIZE
        self.y = self.i * settings.TILE_SIZE
        self.color = color
        self.variety = variety
        self.power_up = power_up
        self.alpha =255
        self.scale = 1.0
        self.alpha_surface = pygame.Surface(
            (settings.TILE_SIZE, settings.TILE_SIZE), pygame.SRCALPHA
        )

    def render(self, surface: pygame.Surface, offset_x: int, offset_y: int) -> None:
        if self.alpha <=0:
            return
        tile_surface = pygame.Surface(
            (settings.TILE_SIZE, settings.TILE_SIZE), pygame.SRCALPHA
        )
        self.alpha_surface.blit(
            settings.TEXTURES["tiles"],
            (0, 0),
            settings.FRAMES["tiles"][self.color][self.variety],
        )
        pygame.draw.rect(
            self.alpha_surface,
            (34, 32, 52, 200),
            pygame.Rect(0, 0, settings.TILE_SIZE, settings.TILE_SIZE),
            border_radius=7,
        )
        surface.blit(self.alpha_surface, (self.x + 2 + offset_x, self.y + 2 + offset_y))
        surface.blit(
            settings.TEXTURES["tiles"],
            (self.x + offset_x, self.y + offset_y),
            settings.FRAMES["tiles"][self.color][self.variety],
        )
        if self.power_up is not None:
            power_rect = pygame.Surface(
                (settings.TILE_SIZE, settings.TILE_SIZE), pygame.SRCALPHA
            )
            if getattr(self.power_up, "kind", "") == "line":
                pygame.draw.rect(
                    power_rect,
                    (0, 240, 255, 140),
                    pygame.Rect(0, 0, settings.TILE_SIZE, settings.TILE_SIZE),
                    border_radius=7,
                    width=3,
                )
            elif getattr(self.power_up, "kind", "") == "color":
                pygame.draw.rect(
                    power_rect,
                    (255, 215, 0, 160),
                    pygame.Rect(0, 0, settings.TILE_SIZE, settings.TILE_SIZE),
                    border_radius=7,
                    width=4,
                )
            tile_surface.blit(power_rect,(0,0))
        
        if self.alpha < 255:
            tile_surface.set_alpha(int(self.alpha))

        if self.scale != 1.0 and self.scale > 0:
            new_size = int(settings.TILE_SIZE * self.scale)
            scaled_surf = pygame.transform.smoothscale(tile_surface, (new_size, new_size))
            offset_scaled_x = (settings.TILE_SIZE - new_size) // 2
            offset_scaled_y = (settings.TILE_SIZE - new_size) // 2
            surface.blit(scaled_surf, (self.x + offset_x + offset_scaled_x, self.y + offset_y + offset_scaled_y))
        else:
            surface.blit(tile_surface, (self.x + offset_x, self.y + offset_y))