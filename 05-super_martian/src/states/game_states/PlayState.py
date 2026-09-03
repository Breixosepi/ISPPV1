"""
ISPPV1 2023
Study Case: Super Martian (Platformer)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class PlayState.
"""

import math
from typing import Dict, Any

import pygame

from gale.camera import Camera
from gale.input_handler import InputData
from gale.state import BaseState
from gale.text import render_text
from gale.timer import Timer

import settings
from src.Clock import Clock
from src.GameLevel import GameLevel
from src.Player import Player
from src.GameItem import GameItem


class PlayState(BaseState):
    def enter(self, **enter_params: Dict[str, Any]) -> None:
        self.level = enter_params.get("level", 1)
        self.game_level = enter_params.get("game_level")
        if self.game_level is None:
            self.game_level = GameLevel(self.level)
            pygame.mixer.music.load(
                settings.BASE_DIR / "assets" / "sounds" / "music_grassland.ogg"
            )
            pygame.mixer.music.play(loops=-1)

        self.tilemap = self.game_level.tilemap
        self.player = enter_params.get("player")
        if self.player is None:
            # Resting exactly on the ground tile's surface (row 9, one tile
            # below the platform's top edge) rather than a few pixels into
            # it, so gale.tilemap's one-way platform collision (which
            # requires the entity to already be at/above the surface) picks
            # it up on the very first frame instead of falling through.
            spawn_y = 9 * self.tilemap.tile_height - 20
            self.player = Player(0, spawn_y, self.game_level)
            self.player.change_state("idle")

        self.camera = enter_params.get("camera")

        if self.camera is None:
            self.camera = Camera(settings.VIRTUAL_WIDTH, settings.VIRTUAL_HEIGHT)
            self.camera.follow(self.player, rate=settings.CAMERA_FOLLOW_RATE)
            self.camera.bounds = self.game_level.get_rect()
            self.camera.x, self.camera.y = self.player.x, self.player.y
            self.camera.update(0)

        self.clock = enter_params.get("clock")

        if self.clock is None:
            self.clock = Clock(30)

            def countdown_timer():
                self.clock.count_down()

                if 0 < self.clock.time <= 5:
                    settings.SOUNDS["timer"].play()

                if self.clock.time == 0:
                    self.player.change_state("dead")

            Timer.every(1, countdown_timer)
        else:
            Timer.resume()

        # --- Iris-out transition state ---
        self.transitioning = False
        # 0.0 = fully open, 1.0 = fully closed
        self.transition_progress = 0.0
        self.countdown_timer_ref = None

    def update(self, dt: float) -> None:
        if self.player.is_dead:
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
            Timer.clear()
            self.state_machine.change("game_over", self.player)
            return

        # If we're in transition, only update the timer (for tween) and return
        if self.transitioning:
            return

        self.player.update(dt)

        if self.player.y >= self.tilemap.pixel_height:
            self.player.change_state("dead")

        self.camera.update(dt)
        self.game_level.update(dt)

        for creature in self.game_level.creatures:
            if self.player.collides(creature):
                self.player.change_state("dead")

        # --- Item collisions ---
        for item in self.game_level.items:
            if not item.active or not item.collidable:
                continue

            if self.player.collides(item):
                # Skip coin consumption if coins are disabled (level ending)
                if self.game_level.coins_disabled and item is not self.game_level.key_item:
                    continue
                item.on_collide(self.player)
                item.on_consume(self.player)

        # --- Key block activation (score threshold reached) ---
        target = settings.TARGET_SCORES.get(self.level, 100)
        if (
            self.player.score >= target
            and self.game_level.key_block_pos is not None
            and not self.game_level.key_block_active
        ):
            col = int(self.game_level.key_block_pos[0] // self.tilemap.tile_width)
            row = int(self.game_level.key_block_pos[1] // self.tilemap.tile_height)
            self.tilemap.set_gid("ground", row, col, settings.KEY_BLOCK_GID)
            self.game_level.key_block_active = True

            bx, by = self.game_level.key_block_pos
            texture = "dungeon_tiles" 
            self.game_level.visual_block = GameItem(
                bx, by, 16, 16, texture, settings.KEY_BLOCK_GID - 1, 
                collidable=False, consumable=False
            )
            self.game_level.items.append(self.game_level.visual_block)
            
            settings.SOUNDS["pickup_coin"].play()

        # --- Hitting the block from below ---
        if self.game_level.key_block_active and not self.game_level.key_spawned:
            bx, by = self.game_level.key_block_pos
            tw = self.tilemap.tile_width
            th = self.tilemap.tile_height

            # Check if player's head is hitting the bottom of the block
            # Player must be moving upward (jumping) and head must touch block
            player_head_y = self.player.y
            player_center_x = self.player.x + self.player.width / 2
            block_bottom = by + th

            # The head must be within a few pixels of the block bottom
            # and the player must be horizontally aligned with the block
            if (
                self.player.vy < 0  # moving upward
                and abs(player_head_y - block_bottom) < 6
                and bx <= player_center_x <= bx + tw
            ):
                # Hit! Spawn the key
                col = int(bx // tw)
                row = int(by // th)
                
                if hasattr(self.game_level, "visual_block"):
                    self.game_level.visual_block.frame_index = settings.KEY_BLOCK_USED_GID - 1
                
                settings.SOUNDS["jump"].play()
                self.game_level.spawn_key()

        # --- Key picked up: start level completion ---
        if self.player.has_key and not self.transitioning:
            self._start_level_transition()

    def _start_level_transition(self) -> None:
        """Begin the iris-out circle transition and stop gameplay."""
        self.transitioning = True
        self.game_level.coins_disabled = True

        # Stop the countdown timer
        Timer.clear()

        # Play level complete sound
        settings.SOUNDS["level_complete"].play()

        # Animate the iris-out transition
        Timer.tween(
            settings.LEVEL_TRANSITION_TIME,
            [(self, {"transition_progress": 1.0})],
            on_finish=self._on_transition_complete,
        )

    def _on_transition_complete(self) -> None:
        """Called when the iris-out finishes; load next level or end game."""
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
        Timer.clear()

        if self.level < settings.NUM_LEVELS:
            self.state_machine.change("play", level=self.level + 1)
        else:
            # Last level completed — show game over with final score
            self.state_machine.change("game_over", self.player)

    def render(self, surface: pygame.Surface) -> None:
        self.game_level.render(surface, self.camera)
        self.player.render(surface, self.camera)

        render_text(
            surface,
            f"Score: {self.player.score}",
            settings.FONTS["small"],
            5,
            5,
            (255, 255, 255),
            shadowed=True,
        )

        render_text(
            surface,
            f"Time: {self.clock.time}",
            settings.FONTS["small"],
            settings.VIRTUAL_WIDTH - 60,
            5,
            (255, 255, 255),
            shadowed=True,
        )

        # Show target score indicator
        if not self.game_level.key_block_active and self.game_level.key_block_pos is not None:
            target = settings.TARGET_SCORES.get(self.level, 100)
            render_text(
                surface,
                f"Target: {target}",
                settings.FONTS["small"],
                settings.VIRTUAL_WIDTH // 2,
                5,
                (255, 255, 100),
                center=True,
                shadowed=True,
            )
        if self.game_level.key_block_active and not self.game_level.key_spawned and self.game_level.key_block_pos is not None:
            bx, by = self.game_level.key_block_pos
            rect = self.camera.apply(pygame.Rect(bx - 2, by - 2, 20, 20))
            pulse = int(150 + 105 * math.sin(pygame.time.get_ticks() * 0.005))
            glow_surf = pygame.Surface((20, 20), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (255, 215, 0, pulse), pygame.Rect(0, 0, 20, 20), width=2, border_radius=4)
            surface.blit(glow_surf, rect)

        # --- Iris-out transition overlay ---
        if self.transitioning and self.transition_progress > 0:
            self._render_iris_out(surface)

    def _render_iris_out(self, surface: pygame.Surface) -> None:
        """Draw a shrinking circle that closes around the player."""
        w = settings.VIRTUAL_WIDTH
        h = settings.VIRTUAL_HEIGHT

        # Create a black overlay surface with alpha support
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 255))

        # Calculate the circle center (player's screen position)
        player_screen = self.camera.apply(
            pygame.Rect(
                self.player.x + self.player.width // 2,
                self.player.y + self.player.height // 2,
                1,
                1,
            )
        )
        cx, cy = player_screen.x, player_screen.y

        # Maximum radius = diagonal of the screen (covers everything when open)
        max_radius = int(math.sqrt(w * w + h * h))
        # Current radius shrinks from max to 0
        radius = int(max_radius * (1.0 - self.transition_progress))

        if radius > 0:
            # Cut a transparent circle hole in the black overlay
            pygame.draw.circle(overlay, (0, 0, 0, 0), (cx, cy), radius)

        surface.blit(overlay, (0, 0))

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if self.transitioning:
            return  # Ignore input during transition

        if input_id == "pause" and input_data.pressed:
            Timer.pause()
            self.state_machine.change(
                "pause",
                level=self.level,
                camera=self.camera,
                game_level=self.game_level,
                player=self.player,
                clock=self.clock,
            )
        else:
            self.player.on_input(input_id, input_data)
