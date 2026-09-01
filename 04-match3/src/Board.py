"""
ISPPV1 2023
Study Case: Match-3

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class Board.
"""

from typing import List, Optional, Tuple, Any, Dict, Set

import pygame

import random

import settings
from src.Tile import Tile
from src.powerups import LinePowerUp, ColorPowerUp
from gale.particle_system import ParticleSystem


class Board:
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y
        self.matches: List[List[Tile]] = []
        self.tiles: List[List[Tile]] = []
        self.particle_systems = []
        self._initialize_tiles()

    def render(self, surface: pygame.Surface) -> None:
        for row in self.tiles:
            for tile in row:
                if tile is not None:
                    tile.render(surface, self.x, self.y)

        for item in self.particle_systems:
            item["ps"].render(surface)

    def _is_match_generated(self, i: int, j: int, color: int) -> bool:
        if (
            i >= 2
            and self.tiles[i - 1][j].color == color
            and self.tiles[i - 2][j].color == color
        ):
            return True

        return (
            j >= 2
            and self.tiles[i][j - 1].color == color
            and self.tiles[i][j - 2].color == color
        )

    def _initialize_tiles(self) -> None:
        self.tiles = [
            [None for _ in range(settings.BOARD_WIDTH)]
            for _ in range(settings.BOARD_HEIGHT)
        ]
        for i in range(settings.BOARD_HEIGHT):
            for j in range(settings.BOARD_WIDTH):
                color = random.randint(0, settings.NUM_COLORS - 1)
                while self._is_match_generated(i, j, color):
                    color = random.randint(0, settings.NUM_COLORS - 1)

                self.tiles[i][j] = Tile(
                    i, j, color, random.randint(0, settings.NUM_VARIETIES - 1)
                )

    def recreate_board(self) -> List[Tuple[Tile, Dict[str, Any]]]:
        self.matches = []
        while True:
            self._initialize_tiles()
            if self.has_valid_move():
                break

        tweens: List[Tuple[Tile, Dict[str, Any]]] = []
        for i in range(settings.BOARD_HEIGHT):
            for j in range(settings.BOARD_WIDTH):
                tile = self.tiles[i][j]
                tile.y = (i - 2) * settings.TILE_SIZE
                tweens.append((tile, {"y": tile.i * settings.TILE_SIZE}))

        return tweens

    def find_valid_move(self) -> Optional[Tuple[int, int, int, int]]:
        for i in range(settings.BOARD_HEIGHT):
            for j in range(settings.BOARD_WIDTH):
                if j + 1 < settings.BOARD_WIDTH:
                    if self._swap_creates_match(i, j, i, j + 1):
                        return i, j, i, j + 1
                if i + 1 < settings.BOARD_HEIGHT:
                    if self._swap_creates_match(i, j, i + 1, j):
                        return i, j, i + 1, j
        return None

    def has_valid_move(self) -> bool:
        return self.find_valid_move() is not None

    def _swap_creates_match(self, i1: int, j1: int, i2: int, j2: int) -> bool:
        if abs(i1 - i2) + abs(j1 - j2) != 1:
            return False

        tile1 = self.tiles[i1][j1]
        tile2 = self.tiles[i2][j2]

        self.tiles[i1][j1] = tile2
        self.tiles[i2][j2] = tile1
        tile1.i, tile1.j, tile2.i, tile2.j = i2, j2, i1, j1

        matches = self.calculate_matches_for([tile1, tile2])
        self.matches = []

        self.tiles[i1][j1] = tile1
        self.tiles[i2][j2] = tile2
        tile1.i, tile1.j = i1, j1
        tile2.i, tile2.j = i2, j2

        return matches is not None
    
    def trigger_power_up_at(self, i: int, j: int) -> Optional[List[List[Tile]]]:
        tile = self.tiles[i][j]
        if tile is None or tile.power_up is None:
            return None

        self.matches = []
        match_group: List[Tile] = []
        self._expand_power_ups_rec(tile, match_group)
        if match_group:
            self.matches.append(match_group)

        return self.matches if len(self.matches) > 0 else None

    def _expand_power_ups_rec(
        self, tile: Tile, current_match: List[Tile], visited_pu: Optional[Set[Tile]] = None
    ) -> None:
        if visited_pu is None:
            visited_pu = set()

        if tile is None or tile in visited_pu:
            return

        visited_pu.add(tile)
        if tile not in current_match:
            current_match.append(tile)

        # Si la ficha tiene un Power-Up, detonamos sus objetivos
        if tile.power_up is not None:
            targets = tile.power_up.targets(self, tile)
            for t in targets:
                if t is not None and t not in visited_pu:
                    self._expand_power_ups_rec(t, current_match, visited_pu)

    def calculate_matches_for(
        self, new_tiles: List[Tile]
    ) -> Optional[List[List[Tile]]]:
        self.in_match: Set[Tile] = set()
        self.in_stack: Set[Tile] = set()

        for tile in new_tiles:
            if tile is None or tile in self.in_match:
                continue
            match = list(self._calculate_match_rec(tile))
            if len(match) > 0:
                self.matches.append(match)

        delattr(self, "in_match")
        delattr(self, "in_stack")

        return self.matches if len(self.matches) > 0 else None

    def _calculate_match_rec(self, tile: Tile) -> Set[Tile]:
        if tile in self.in_stack or tile is None:
            return set()

        self.in_stack.add(tile)
        color_to_match = tile.color

        h_match: List[Tile] = []

        # Check left
        if tile.j > 0:
            left = max(0, tile.j - 2)
            for j in range(tile.j - 1, left - 1, -1):
                t = self.tiles[tile.i][j]
                if t is None or t.color != color_to_match:
                    break
                h_match.append(t)

        # Check right
        if tile.j < settings.BOARD_WIDTH - 1:
            right = min(settings.BOARD_WIDTH - 1, tile.j + 2)
            for j in range(tile.j + 1, right + 1):
                t = self.tiles[tile.i][j]
                if t is None or t.color != color_to_match:
                    break
                h_match.append(t)

        v_match: List[Tile] = []

        # Check top
        if tile.i > 0:
            top = max(0, tile.i - 2)
            for i in range(tile.i - 1, top - 1, -1):
                t = self.tiles[i][tile.j]
                if t is None or t.color != color_to_match:
                    break
                v_match.append(t)

        # Check bottom
        if tile.i < settings.BOARD_HEIGHT - 1:
            bottom = min(settings.BOARD_HEIGHT - 1, tile.i + 2)
            for i in range(tile.i + 1, bottom + 1):
                t = self.tiles[i][tile.j]
                if t is None or t.color != color_to_match:
                    break
                v_match.append(t)

        match: List[Tile] = []

        if len(h_match) >= 2:
            for t in h_match:
                if t not in self.in_match:
                    self.in_match.add(t)
                    match.append(t)

        if len(v_match) >= 2:
            for t in v_match:
                if t not in self.in_match:
                    self.in_match.add(t)
                    match.append(t)

        if len(match) > 0:
            if tile not in self.in_match:
                self.in_match.add(tile)
                match.append(tile)

        additional: List[Tile] = []
        visited_pu: Set[Tile] = set()
        for t in list(match):
            if t.power_up is not None:
                self._expand_power_ups_rec(t, additional, visited_pu)

        for t in additional:
            if t not in match:
                match.append(t)

        self.in_stack.remove(tile)
        return set(match)
    
    def remove_matches(self, target_position: Optional[Tuple[int, int]] = None) -> None:
        new_power_up_info = None
        for match in self.matches:
            match_list = list(match) if isinstance(match, (set, tuple)) else match
            
            has_existing_booster = False
            booster_kind = None
            for t in match_list:
                if t is not None and getattr(t, 'power_up', None) is not None:
                    has_existing_booster = True
                    booster_kind = getattr(t.power_up, "kind", "line")
                    break

            if len(match_list) >= 4 and not has_existing_booster:
                spawn_i, spawn_j = -1, -1
                if target_position is not None:
                    ti, tj = target_position
                    for t in match_list:
                        if t.i == ti and t.j == tj:
                            spawn_i, spawn_j = ti, tj
                            break
                if spawn_i == -1 or spawn_j == -1:
                    spawn_i, spawn_j = match_list[0].i, match_list[0].j
                color = match_list[0].color
                variety = match_list[0].variety
                if len(match_list) == 4:
                    pu = LinePowerUp()
                else:
                    pu = ColorPowerUp()
                new_power_up_info = (spawn_i, spawn_j, color, variety, pu)
            
            for tile in match_list:
                if tile is not None and 0 <= tile.i < settings.BOARD_HEIGHT and 0 <= tile.j < settings.BOARD_WIDTH:
                    
                    if has_existing_booster and booster_kind is not None:
                        self._spawn_particles(tile, booster_kind)
                        
                    self.tiles[tile.i][tile.j] = None
                    
        self.matches = []
        if new_power_up_info is not None:
            i, j, color, variety, pu = new_power_up_info
            tile = Tile(i, j, color, variety, power_up=pu)
            pu.tile = tile
            self.tiles[i][j] = tile

    def get_falling_tiles(self) -> Tuple[Any, Dict[str, Any]]:
        tweens: Tuple[Tile, Dict[str, Any]] = []

        for j in range(settings.BOARD_WIDTH):
            space = False
            space_i = -1
            i = settings.BOARD_HEIGHT - 1

            while i >= 0:
                tile = self.tiles[i][j]

                if space:
                    if tile is not None:
                        self.tiles[space_i][j] = tile
                        tile.i = space_i

                        self.tiles[i][j] = None

                        tweens.append((tile, {"y": tile.i * settings.TILE_SIZE}))
                        space = False
                        i = space_i
                        space_i = -1
                elif tile is None:
                    space = True

                    if space_i == -1:
                        space_i = i

                i -= 1

        for j in range(settings.BOARD_WIDTH):
            for i in range(settings.BOARD_HEIGHT):
                tile = self.tiles[i][j]

                if tile is None:
                    tile = Tile(
                        i,
                        j,
                        random.randint(0, settings.NUM_COLORS - 1),
                        random.randint(0, settings.NUM_VARIETIES - 1),
                    )
                    tile.y -= settings.TILE_SIZE
                    self.tiles[i][j] = tile
                    tweens.append((tile, {"y": tile.i * settings.TILE_SIZE}))

        return tweens

    def _spawn_particles(self, tile: Tile, kind: str) -> None:
        state = {"active": True}
        def on_finish():
            state["active"] = False
        
        px = tile.x + self.x + settings.TILE_SIZE // 2
        py = tile.y + self.y + settings.TILE_SIZE // 2
        
        ps = ParticleSystem(px, py, 30, on_finish) 
        ps.set_life_time(0.8, 1.4) 
        
        if kind == "line":
            ps.set_linear_acceleration(-150, 150, -150, 150)
            ps.set_area_spread(4, 4)
            ps.set_colors([(0, 240, 255, 255), (0, 240, 255, 0)])

        elif kind == "color":
            ps.set_linear_acceleration(-100, 100, -100, 100)
            ps.set_area_spread(10, 10)
            ps.set_colors([(255, 215, 0, 255), (255, 215, 0, 0)])
        
        ps.generate()
        self.particle_systems.append({"ps": ps, "state": state})

    def update(self, dt: float) -> None:

        alive_particles = []

        for item in self.particle_systems:
            item["ps"].update(dt)
            if item["state"]["active"]:
                alive_particles.append(item)

        self.particle_systems = alive_particles