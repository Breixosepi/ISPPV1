"""
ISPPV1 2026
Study Case: The Legend of the Princess (ARPG)

Author: Eugenio Montilla
eugeniorusso1411@gmail.com

This file contains the class PlayerSwingSwordState.
"""

from typing import TypeVar

import pygame

from gale.state import StateMachine

import settings
from src.states.entity.BaseEntityState import BaseEntityState


class PlayerSwingSwordState(BaseEntityState):
    def __init__(
        self,
        player: TypeVar("Player"),
        state_machine: StateMachine,
        dungeon: TypeVar("Dungeon"),
    ) -> None:
        super().__init__(player, state_machine)
        self.dungeon = dungeon

        self.entity.offset_y = 5
        self.entity.offset_x = 8

        direction = self.entity.direction

        if direction == "left":
            width, height = 8, 16
            x = self.entity.x - width
            y = self.entity.y + 2
        elif direction == "right":
            width, height = 8, 16
            x = self.entity.x + self.entity.width
            y = self.entity.y + 2
        elif direction == "up":
            width, height = 16, 8
            x = self.entity.x
            y = self.entity.y - height
        else:
            width, height = 16, 8
            x = self.entity.x
            y = self.entity.y + self.entity.height

        self.sword_hitbox = pygame.Rect(round(x), round(y), width, height)
        self.entity.change_animation(f"sword-{direction}")

    def enter(self) -> None:
        settings.SOUNDS["sword"].stop()
        settings.SOUNDS["sword"].play()

        # Restart sword swing animation.
        self.entity.current_animation.reset()

    def update(self, dt: float) -> None:
        self.entity.interact_requested = False

        if self.entity.sword_requested:
            self.entity.sword_requested = False
            self.entity.change_state("swing-sword")
            return

        for entity in self.dungeon.current_room.entities:
            if entity.collides(self.sword_hitbox):
                room = self.dungeon.current_room
                if room.is_boss_room and room._boss and entity == room._boss:
                    if not room._boss_immune:
                        entity.damage(1)
                        settings.SOUNDS["hit-enemy"].play()
                        room._boss_immune = True 
                else:
                    entity.damage(1)
                    settings.SOUNDS["hit-enemy"].play()

        if self.entity.current_animation.times_played > 0:
            self.entity.current_animation.times_played = 0
            self.entity.change_state("idle")

    def render(self, surface: pygame.Surface) -> None:
        anim = self.entity.current_animation
        self.entity.render_sprite(surface, anim.texture_id, anim.get_current_frame())
