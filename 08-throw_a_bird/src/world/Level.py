"""
ISPPV1 2023
Study Case: Throw a Bird

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class Level: the static ground, the tower of
stone/wood/alien blocks, the two wind boundary zones, and the parallax
background -- everything in the original Defold .collection except the
parrot itself and the camera/input logic (both PlayState's concerns).

Layout numbers (ground extents, block positions) are lifted straight
from the brief's read-out of the original .collection, in Defold's Y-up,
level-local pixels; settings.flip_y() converts every Y to gale/pygame's
Y-down convention. x is unaffected by the flip. None of this is meant to
be pixel-perfect -- per the brief, it is a recreation, not a port of
exact numbers.
"""

import math
import random
from typing import List, Tuple

import pygame

from gale.physics.shapes import BoxShape
from gale.physics.world import World

import settings
from src.entity.Debris import DebrisChip
from src.entity.Destructible import Destructible
from src.world.Background import Background

# name, x, y (Defold Y-up, level-local), archetype, rotated 90 degrees
BLOCKS: List[Tuple[str, float, float, str, bool]] = [
    ("stone0", 2062, 145, "stone", False),
    ("stone1", 2247, 145, "stone", False),
    ("stone2", 2467, 145, "stone", False),
    ("stone3", 2652, 145, "stone", False),
    ("wood0", 2137, 215, "wood", False),
    ("wood1", 2357, 215, "wood", False),
    ("wood2", 2577, 215, "wood", False),
    ("stone4", 2062, 285, "stone", False),
    ("stone5", 2247, 285, "stone", False),
    ("stone6", 2467, 285, "stone", False),
    ("stone7", 2652, 285, "stone", False),
    ("wood3", 2062, 430, "wood", True),
    ("wood4", 2247, 430, "wood", True),
    ("wood6", 2467, 430, "wood", True),
    ("wood5", 2652, 430, "wood", True),
    ("stone8", 2062, 575, "stone", False),
    ("stone9", 2247, 575, "stone", False),
    ("stone10", 2467, 575, "stone", False),
    ("stone11", 2652, 575, "stone", False),
    ("wood7", 2137, 645, "wood", False),
    ("wood8", 2357, 645, "wood", False),
    ("wood9", 2577, 645, "wood", False),
    ("wood10", 2282, 790, "wood", True),
    ("wood11", 2432, 790, "wood", True),
    ("wood12", 2357, 935, "wood", False),
    ("alien_round0", 2357, 715, "alien_round", False),
    ("alien_round1", 2357, 1005, "alien_round", False),
    ("stone12", 2282, 1005, "stone", False),
    ("stone13", 2432, 1005, "stone", False),
    ("alien_square0", 2154, 285, "alien_square", False),
    ("alien_square1", 2357, 145, "alien_square", False),
    ("alien_square2", 2559, 285, "alien_square", False),
]

# Ground world-space center and half-extents, taken directly from the
# brief (ground instance position (512, 295) + local collision-shape
# offset (1377, -223), half-extents 6448.155 x 36.718).
GROUND_CENTER_X = 1889
GROUND_TOP_DEFOLD_Y = 72 + 36.718
GROUND_HALF_WIDTH = 6448.155
# Thickened well past the original's thin collision box, purely so the
# ground reads as a solid slab instead of a sliver (there is no floor
# graphic below the visible strip otherwise).
GROUND_VISUAL_HEIGHT = 600.0

BIRD_START_DEFOLD = (300, 300)

WIND_ZONE_MARGIN = 200.0
WIND_ZONE_WIDTH = 150.0
WIND_ZONE_HEIGHT = 6000.0
# A flat force (not scaled by the body's own mass), matching the
# original wind.script applying the same physics.apply_force vector to
# whatever it touches -- so, exactly like the original, this pushes
# light objects (a wood plank) proportionally harder than heavy ones
# (the bird), which is the point: a soft boundary that reliably turns
# anything back, regardless of what it is.
WIND_FORCE = 2_500_000.0

DEBRIS_PER_BLOCK = 5
DEBRIS_SCATTER = 30


class Level:
    def __init__(self, world: World) -> None:
        self.world = world
        self.background = Background()
        self.blocks: List[Destructible] = []
        self.debris: List[DebrisChip] = []

        self._build_ground()
        self._build_blocks()
        self._build_wind_zones()

    @property
    def bird_start(self) -> pygame.Vector2:
        x, y = BIRD_START_DEFOLD
        return pygame.Vector2(x, settings.flip_y(y))

    @property
    def ground_x_range(self) -> Tuple[float, float]:
        return (
            GROUND_CENTER_X - GROUND_HALF_WIDTH,
            GROUND_CENTER_X + GROUND_HALF_WIDTH,
        )

    def _build_ground(self) -> None:
        self.ground_top_y = settings.flip_y(GROUND_TOP_DEFOLD_Y)
        center_y = self.ground_top_y + GROUND_VISUAL_HEIGHT / 2

        self.ground_body = self.world.create_static_body(
            GROUND_CENTER_X,
            center_y,
            BoxShape(GROUND_HALF_WIDTH * 2, GROUND_VISUAL_HEIGHT, friction=1.0),
        )
        self.ground_body.user_data = "ground"

    def _build_blocks(self) -> None:
        for _name, dx, dy, archetype, rot90 in BLOCKS:
            angle = math.pi / 2 if rot90 else 0.0
            self.blocks.append(
                Destructible(self.world, dx, settings.flip_y(dy), archetype, angle)
            )

    def _build_wind_zones(self) -> None:
        left, right = self.ground_x_range
        center_y = self.ground_top_y - WIND_ZONE_HEIGHT / 2 + 400

        self.wind_left = self.world.create_static_body(
            left - WIND_ZONE_MARGIN,
            center_y,
            BoxShape(WIND_ZONE_WIDTH, WIND_ZONE_HEIGHT, is_sensor=True),
        )
        self.wind_left.user_data = "wind"

        self.wind_right = self.world.create_static_body(
            right + WIND_ZONE_MARGIN,
            center_y,
            BoxShape(WIND_ZONE_WIDTH, WIND_ZONE_HEIGHT, is_sensor=True),
        )
        self.wind_right.user_data = "wind"

    def update(self, dt: float) -> None:
        self._apply_wind()
        self._collect_destroyed()
        self.debris = [chip for chip in self.debris if chip.alive]

    def _apply_wind(self) -> None:
        for wind_body, sign in ((self.wind_left, 1), (self.wind_right, -1)):
            for body in wind_body.touching_bodies:
                body.apply_force(sign * WIND_FORCE, 0)

    def _collect_destroyed(self) -> None:
        survivors = []

        for block in self.blocks:
            if not block.destroyed:
                survivors.append(block)
                continue

            if block.spawns_debris:
                position = block.position
                for _ in range(DEBRIS_PER_BLOCK):
                    offset_x = random.uniform(-DEBRIS_SCATTER, DEBRIS_SCATTER)
                    offset_y = random.uniform(-DEBRIS_SCATTER, DEBRIS_SCATTER)
                    self.debris.append(
                        DebrisChip(position.x + offset_x, position.y + offset_y)
                    )

            self.world.destroy_body(block.body)

        self.blocks = survivors

    def handle_collision(self, body_a, body_b) -> None:
        self._handle_pair(body_a, body_b)
        self._handle_pair(body_b, body_a)

    def _handle_pair(self, body, other) -> None:
        entity = body.user_data

        if not isinstance(entity, Destructible):
            return

        if other.user_data == "ground":
            entity.on_collision(other, is_ground=True)
        elif other.user_data == "wind":
            return
        elif hasattr(other.user_data, "mass"):
            entity.on_collision(other, is_ground=False)

    def render(self, surface: pygame.Surface, camera) -> None:
        self.background.render(surface, camera)
        self._render_ground(surface, camera)

        for block in self.blocks:
            block.render(surface, camera)

        for chip in self.debris:
            chip.render(surface, camera)

    def _render_ground(self, surface: pygame.Surface, camera) -> None:
        top_screen_y = round((self.ground_top_y - camera.offset[1]) * camera.zoom)
        fill_rect = pygame.Rect(
            0, max(0, top_screen_y), surface.get_width(), surface.get_height()
        )
        pygame.draw.rect(surface, settings.GROUND_FILL_COLOR, fill_rect)

        strip = settings.TEXTURES["ground-strip"]
        strip_width, strip_height = strip.get_size()
        size = (
            max(1, round(strip_width * camera.zoom)),
            max(1, round(strip_height * camera.zoom)),
        )
        scaled_strip = pygame.transform.scale(strip, size)

        left, right = self.ground_x_range
        x = left

        while x < right:
            center = (x + strip_width / 2, self.ground_top_y + strip_height / 2)
            rect = scaled_strip.get_rect(center=camera.world_to_screen(center))

            if rect.right >= 0 and rect.left <= surface.get_width():
                surface.blit(scaled_strip, rect)

            x += strip_width
