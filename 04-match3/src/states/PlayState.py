"""
ISPPV1 2023
Study Case: Match-3

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class PlayState.
"""

from typing import Dict, Any, List

import pygame

from gale.input_handler import InputData
from gale.state import BaseState
from gale.text import render_text
from gale.timer import Timer

import settings


class PlayState(BaseState):
    def enter(self, **enter_params: Dict[str, Any]) -> None:
        self.level = enter_params["level"]
        self.board = enter_params["board"]
        self.score = enter_params["score"]

        # Position in the grid which we are highlighting
        self.board_highlight_i1 = -1
        self.board_highlight_j1 = -1
        self.board_highlight_i2 = -1
        self.board_highlight_j2 = -1

        self.highlighted_tile = False

        self.dragging = False
        self.drag_tile = None
        self.drag_origin_i = -1
        self.drag_origin_j = -1

        self.active = True

        self.timer = settings.LEVEL_TIME

        self.goal_score = self.level * 1.25 * 1000

        # A surface that supports alpha to highlight a selected tile
        self.tile_alpha_surface = pygame.Surface(
            (settings.TILE_SIZE, settings.TILE_SIZE), pygame.SRCALPHA
        )
        pygame.draw.rect(
            self.tile_alpha_surface,
            (255, 255, 255, 96),
            pygame.Rect(0, 0, settings.TILE_SIZE, settings.TILE_SIZE),
            border_radius=7,
        )

        # A surface that supports alpha to draw behind the text.
        self.text_alpha_surface = pygame.Surface((212, 136), pygame.SRCALPHA)
        pygame.draw.rect(
            self.text_alpha_surface, (56, 56, 56, 234), pygame.Rect(0, 0, 212, 136)
        )

        def decrement_timer():
            self.timer -= 1

            # Play warning sound on timer if we get low
            if self.timer <= 5:
                settings.SOUNDS["clock"].play()

        Timer.every(1, decrement_timer)

    def update(self, _: float) -> None:
        if self.timer <= 0:
            Timer.clear()
            settings.SOUNDS["game-over"].play()
            self.state_machine.change("game-over", score=self.score)

        if self.score >= self.goal_score:
            Timer.clear()
            settings.SOUNDS["next-level"].play()
            self.state_machine.change("begin", level=self.level + 1, score=self.score)

    def render(self, surface: pygame.Surface) -> None:
        self.board.render(surface)

        if self.highlighted_tile:
            x = self.highlighted_j1 * settings.TILE_SIZE + self.board.x
            y = self.highlighted_i1 * settings.TILE_SIZE + self.board.y
            surface.blit(self.tile_alpha_surface, (x, y))

        surface.blit(self.text_alpha_surface, (16, 16))
        render_text(
            surface,
            f"Level: {self.level}",
            settings.FONTS["medium"],
            30,
            24,
            (99, 155, 255),
            shadowed=True,
        )
        render_text(
            surface,
            f"Score: {self.score}",
            settings.FONTS["medium"],
            30,
            52,
            (99, 155, 255),
            shadowed=True,
        )
        render_text(
            surface,
            f"Goal: {self.goal_score}",
            settings.FONTS["medium"],
            30,
            80,
            (99, 155, 255),
            shadowed=True,
        )
        render_text(
            surface,
            f"Timer: {self.timer}",
            settings.FONTS["medium"],
            30,
            108,
            (99, 155, 255),
            shadowed=True,
        )

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if not self.active:
            return

        if input_id == "touch":
            self._on_touch(input_data)
        elif input_id == "touch_motion":
            self._on_touch_motion(input_data)

    def _mouse_to_virtual(self, position) -> pygame.Vector2:
        scale_x = settings.VIRTUAL_WIDTH / settings.WINDOW_WIDTH
        scale_y = settings.VIRTUAL_HEIGHT / settings.WINDOW_HEIGHT
        return pygame.Vector2(position[0] * scale_x, position[1] * scale_y)

    def _cell_from_mouse(self, position: pygame.Vector2):
        x = position.x - self.board.x
        y = position.y - self.board.y
        i = y // settings.TILE_SIZE
        j = x // settings.TILE_SIZE

        if 0 <= i < settings.BOARD_HEIGHT and 0 <= j < settings.BOARD_WIDTH:
            return i, j

        return None

    def _on_touch(self, input_data: InputData) -> None:
        position = self._mouse_to_virtual(input_data.position)

        if input_data.pressed:
            cell = self._cell_from_mouse(position)
            if cell is None:
                return

            i, j = cell
            tile = self.board.tiles[i][j]
            self.dragging = True
            self.drag_tile = tile
            self.drag_origin_i = i
            self.drag_origin_j = j
            self.highlighted_tile = True
            self.highlighted_i1 = i
            self.highlighted_j1 = j
            self.drag_tile.x = position.x - self.board.x
            self.drag_tile.y = position.y - self.board.y
        elif input_data.released:
            if not self.dragging or self.drag_tile is None:
                return

            position = self._mouse_to_virtual(input_data.position)
            target = self._cell_from_mouse(position)
            self.dragging = False
            self.highlighted_tile = False

            if target is None:
                self._reset_drag_tile()
                return

            target_i, target_j = target
            di = abs(target_i - self.drag_origin_i)
            dj = abs(target_j - self.drag_origin_j)

            if di <= 1 and dj <= 1 and di != dj:
                self.active = False
                tile1 = self.board.tiles[self.drag_origin_i][self.drag_origin_j]
                tile2 = self.board.tiles[target_i][target_j]

                tile1.x = tile1.j * settings.TILE_SIZE
                tile1.y = tile1.i * settings.TILE_SIZE
                tile2.x = tile2.j * settings.TILE_SIZE
                tile2.y = tile2.i * settings.TILE_SIZE

                def arrive():
                    tile1 = self.board.tiles[self.drag_origin_i][self.drag_origin_j]
                    tile2 = self.board.tiles[target_i][target_j]
                    (
                        self.board.tiles[tile1.i][tile1.j],
                        self.board.tiles[tile2.i][tile2.j],
                    ) = (
                        self.board.tiles[tile2.i][tile2.j],
                        self.board.tiles[tile1.i][tile1.j],
                    )
                    tile1.i, tile1.j, tile2.i, tile2.j = (
                        tile2.i,
                        tile2.j,
                        tile1.i,
                        tile1.j,
                    )
                    self.drag_tile = None
                    self._calculate_matches([tile1, tile2])

                Timer.tween(
                    0.25,
                    [
                        (tile1, {"x": tile2.x, "y": tile2.y}),
                        (tile2, {"x": tile1.x, "y": tile1.y}),
                    ],
                    on_finish=arrive,
                )
            else:
                self._reset_drag_tile()

            self.drag_tile = None

    def _on_touch_motion(self, input_data: InputData) -> None:
        if not self.dragging or self.drag_tile is None:
            return

        position = self._mouse_to_virtual(input_data.position)
        self.drag_tile.x = position.x - self.board.x
        self.drag_tile.y = position.y - self.board.y

    def _reset_drag_tile(self) -> None:
        if self.drag_tile is None:
            return

        self.drag_tile.x = self.drag_tile.j * settings.TILE_SIZE
        self.drag_tile.y = self.drag_tile.i * settings.TILE_SIZE
        self.drag_tile = None
        self.dragging = False

    def _calculate_matches(self, tiles: List) -> None:
        matches = self.board.calculate_matches_for(tiles)

        if matches is None:
            self.active = True
            return

        settings.SOUNDS["match"].stop()
        settings.SOUNDS["match"].play()

        for match in matches:
            self.score += len(match) * 50

        self.board.remove_matches()

        falling_tiles = self.board.get_falling_tiles()

        Timer.tween(
            0.25,
            falling_tiles,
            on_finish=lambda: self._calculate_matches(
                [item[0] for item in falling_tiles]
            ),
        )
