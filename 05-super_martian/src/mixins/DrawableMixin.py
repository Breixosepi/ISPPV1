"""
ISPPV1 2026
Study Case: Super Martian (Platformer)

Author: Eugenio Montilla
eugeniorusso1411@gmail.com

This file contains the DrawableMixin.
"""

from typing import Any, Dict, Tuple

import pygame

import settings

_FLIPPED_CACHE: Dict[Tuple[str, int], pygame.Surface] = {}


class DrawableMixin:
    def render(self, surface: pygame.Surface, camera: Any) -> None:
        texture = settings.TEXTURES[self.texture_id]
        frame = settings.FRAMES[self.texture_id][self.frame_index]
        dest = camera.apply(pygame.Rect(self.x, self.y, self.width, self.height))

        if not self.flipped:
            surface.blit(texture, dest, area=frame)
        else:
            cache_key = (self.texture_id, self.frame_index)
            flipped_image = _FLIPPED_CACHE.get(cache_key)
            if flipped_image is None:
                flipped_image = pygame.Surface(
                    (frame.width, frame.height), pygame.SRCALPHA
                )
                flipped_image.blit(texture, (0, 0), frame)
                flipped_image = pygame.transform.flip(flipped_image, True, False)
                _FLIPPED_CACHE[cache_key] = flipped_image
            surface.blit(flipped_image, dest)

