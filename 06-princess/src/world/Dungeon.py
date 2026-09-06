"""
ISPPV1 2026
Study Case: The Legend of the Princess (ARPG)

Author: Eugenio Montilla
eugeniorusso1411@gmail.com

This file contains the class Dungeon.
"""

import math
import random
from typing import Callable, TypeVar

import pygame

from gale.timer import Timer

import settings
from src.world.Room import Room, _BOSS_ROOM_CHANCE, _CHEST_SPAWN_CHANCE


class Dungeon:
    def __init__(
        self,
        player: TypeVar("Player"),
        on_game_over: Callable[[], None],
    ) -> None:
        self.player = player
        self.on_game_over = on_game_over

        self._chest_pending = False

        self.current_room = Room(
            self.player,
            self.on_game_over,
            spawn_chest=self._should_spawn_chest(),
        )

        self.next_room = None
        self.camera_x = 0
        self.camera_y = 0
        self.shifting = False


    def _should_spawn_chest(self) -> bool:
        if self.player.has_bow:
            return False
        if self._chest_pending:
            return True
        return random.randint(1, _CHEST_SPAWN_CHANCE) == 1

    def _update_chest_state(self) -> None:
        if self.player.has_bow:
            self._chest_pending = False
            return

        chest = self.current_room._chest
        if chest and chest.state != "open":
            self._chest_pending = True
        else:
            self._chest_pending = False


    def begin_shifting(self, shift_x: float, shift_y: float) -> None:
        """
        Prepares for the camera shifting process, kicking off a tween of the
        camera position. Triggered via a doorway collision, from
        PlayerWalkState/PlayerPotWalkState.
        """
        self.shifting = True

        if shift_x > 0:
            entry_direction = "left"
        elif shift_x < 0:
            entry_direction = "right"
        elif shift_y > 0:
            entry_direction = "up"
        else:
            entry_direction = "down"

        if self.player.has_bow:
            self._rooms_since_bow = getattr(self, "_rooms_since_bow", 0) + 1
        
        is_boss = False
        if self.player.has_bow and not self.current_room.is_boss_room:
            if random.randint(1, _BOSS_ROOM_CHANCE) == 1 or getattr(self, "_rooms_since_bow", 0) >= 4:
                is_boss = True
                self._rooms_since_bow = 0

        self._update_chest_state()

        spawn_chest = False if is_boss else self._should_spawn_chest()

        self.next_room = Room(
            self.player,
            self.on_game_over,
            is_boss_room=is_boss,
            entry_direction=entry_direction,
            spawn_chest=spawn_chest,
        )

        for doorway in self.next_room.doorways:
            doorway.open = True

        self.next_room.adjacent_offset_x = shift_x
        self.next_room.adjacent_offset_y = shift_y

        player_x, player_y = self.player.x, self.player.y

        if shift_x > 0:
            player_x = settings.VIRTUAL_WIDTH + (
                settings.MAP_RENDER_OFFSET_X + settings.TILE_SIZE
            )
        elif shift_x < 0:
            player_x = -settings.VIRTUAL_WIDTH + (
                settings.MAP_RENDER_OFFSET_X
                + settings.MAP_WIDTH * settings.TILE_SIZE
                - settings.TILE_SIZE
                - self.player.width
            )
        elif shift_y > 0:
            player_y = settings.VIRTUAL_HEIGHT + (
                settings.MAP_RENDER_OFFSET_Y + self.player.height / 2
            )
        else:
            player_y = -settings.VIRTUAL_HEIGHT + settings.MAP_RENDER_OFFSET_Y + (
                settings.MAP_HEIGHT * settings.TILE_SIZE
                - settings.TILE_SIZE
                - self.player.height
            )

        to_tween = [
            (self, {"camera_x": shift_x, "camera_y": shift_y}),
            (self.player, {"x": player_x, "y": player_y}),
        ]

        pot = getattr(self.player.state_machine.current, "pot", None)

        if pot is not None:
            to_tween.append((pot, {"x": player_x, "y": player_y - pot.height / 2}))

        Timer.tween(1, to_tween, on_finish=self._finish_shifting_and_place_player)

    def _finish_shifting_and_place_player(self) -> None:
        shift_x = self.camera_x
        shift_y = self.camera_y

        self._finish_shifting()

        if shift_x < 0:
            self.player.x = (
                settings.MAP_RENDER_OFFSET_X
                + settings.MAP_WIDTH * settings.TILE_SIZE
                - settings.TILE_SIZE
                - self.player.width
            )
            self.player.direction = "left"
        elif shift_x > 0:
            self.player.x = settings.MAP_RENDER_OFFSET_X + settings.TILE_SIZE
            self.player.direction = "right"
        elif shift_y < 0:
            self.player.y = (
                settings.MAP_RENDER_OFFSET_Y
                + settings.MAP_HEIGHT * settings.TILE_SIZE
                - settings.TILE_SIZE
                - self.player.height
            )
            self.player.direction = "up"
        else:
            self.player.y = settings.MAP_RENDER_OFFSET_Y + self.player.height / 2
            self.player.direction = "down"

        # was just swapped to it by _finish_shifting above) — they were
        for doorway in self.current_room.doorways:
            doorway.open = False

        self.player.go_invulnerable(1)

        settings.SOUNDS["door"].play()
        if self.current_room.is_boss_room:
            pygame.mixer.music.load(settings.MUSIC["boss"])
            pygame.mixer.music.play(-1)
        elif not self.current_room.is_boss_room and getattr(self, '_last_was_boss', False):
            pygame.mixer.music.load(settings.MUSIC["dungeon"])
            pygame.mixer.music.play(-1)
        self._last_was_boss = self.current_room.is_boss_room

    def _finish_shifting(self) -> None:
        """
        Resets a few variables needed to perform a camera shift and swaps
        the next and current room.
        """
        self.camera_x = 0
        self.camera_y = 0
        self.shifting = False
        self.current_room = self.next_room
        self.next_room = None
        self.current_room.adjacent_offset_x = 0
        self.current_room.adjacent_offset_y = 0

    def update(self, dt: float) -> None:
        # Pause updating if we're in the middle of shifting.
        if not self.shifting:
            self.current_room.update(dt)
        else:
            if self.player.current_animation:
                self.player.current_animation.update(dt)

    def render(self, surface: pygame.Surface) -> None:
        offset_x = -math.floor(self.camera_x)
        offset_y = -math.floor(self.camera_y)

        self.current_room.render(surface, offset_x, offset_y)

        if self.next_room:
            self.next_room.render(surface, offset_x, offset_y)
