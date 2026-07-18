"""
ISPPV1 2023
Study Case: The Legend of the Princess (ARPG)

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class Room.
"""

import random
from typing import Any, Callable, List, Optional, TypeVar

import pygame

import settings
from src.definitions.entity import ENTITY_DEFS
from src.definitions.game_objects import GAME_OBJECT_DEFS
from src.Entity import Entity
from src.GameObject import GameObject
from src.states.entity.EntityIdleState import EntityIdleState
from src.states.entity.EntityWalkState import EntityWalkState
from src.world.Doorway import Doorway

_ENEMY_TYPES = ["skeleton", "slime", "bat", "ghost", "spider"]

# Door archway thresholds, in the same room-local coordinates as every
# entity's x/y (not screen space, so this works regardless of camera/
# adjacent-room render offsets). The player/projectiles are simply not
# drawn while overlapping one of these — the original used a stencil test
# to cut this same archway shape out of the player draw, so walking (or,
# mid room-shift, tweening) through the wall opening never shows them
# clipping through solid wall.
_DOORWAY_ZONES = [
    pygame.Rect(
        -settings.TILE_SIZE - 6,
        settings.MAP_RENDER_OFFSET_Y + settings.MAP_HEIGHT // 2 * settings.TILE_SIZE - settings.TILE_SIZE * 2,
        settings.TILE_SIZE * 2 + 6,
        settings.TILE_SIZE * 3,
    ),
    pygame.Rect(
        settings.MAP_RENDER_OFFSET_X + settings.MAP_WIDTH * settings.TILE_SIZE - 6,
        settings.MAP_RENDER_OFFSET_Y + settings.MAP_HEIGHT // 2 * settings.TILE_SIZE - settings.TILE_SIZE * 2,
        settings.TILE_SIZE * 2 + 6,
        settings.TILE_SIZE * 3,
    ),
    pygame.Rect(
        settings.MAP_RENDER_OFFSET_X + settings.MAP_WIDTH // 2 * settings.TILE_SIZE - settings.TILE_SIZE,
        -settings.TILE_SIZE - 6,
        settings.TILE_SIZE * 2,
        settings.TILE_SIZE * 2 + 12,
    ),
    pygame.Rect(
        settings.MAP_RENDER_OFFSET_X + settings.MAP_WIDTH // 2 * settings.TILE_SIZE - settings.TILE_SIZE,
        settings.VIRTUAL_HEIGHT - settings.TILE_SIZE - 6,
        settings.TILE_SIZE * 2,
        settings.TILE_SIZE * 2 + 12,
    ),
]


def _in_any_doorway_zone(rect: pygame.Rect) -> bool:
    return any(zone.colliderect(rect) for zone in _DOORWAY_ZONES)


class Room:
    def __init__(
        self,
        player: TypeVar("Player"),
        on_game_over: Callable[[], None],
    ) -> None:
        # Reference to player for collisions, etc.
        self.player = player
        self.on_game_over = on_game_over

        self.width = settings.MAP_WIDTH
        self.height = settings.MAP_HEIGHT

        self.tiles: List[List[int]] = []
        self._generate_walls_and_floors()

        self.entities: List[Entity] = []
        self._generate_entities()

        self.objects: List[GameObject] = []
        self._generate_objects()

        # Doorways that lead to other dungeon rooms.
        self.doorways = [
            Doorway("top", False, self),
            Doorway("bottom", False, self),
            Doorway("left", False, self),
            Doorway("right", False, self),
        ]

        # Used for centering the dungeon rendering.
        self.render_offset_x = settings.MAP_RENDER_OFFSET_X
        self.render_offset_y = settings.MAP_RENDER_OFFSET_Y

        # Used for drawing when this room is the next room, adjacent to the
        # active one, while sliding between rooms.
        self.adjacent_offset_x = 0
        self.adjacent_offset_y = 0

        self.projectiles: List[Any] = []

    def update(self, dt: float) -> None:
        # Don't update anything if we are sliding to another room.
        if self.adjacent_offset_x != 0 or self.adjacent_offset_y != 0:
            return

        self.player.update(dt)

        for entity in self.entities:
            if entity.health <= 0:
                entity.dead = True

                # Chance to drop a heart.
                if not entity.dropped and random.randint(1, 10) == 1:
                    self.objects.append(
                        GameObject(GAME_OBJECT_DEFS["heart"], entity.x, entity.y)
                    )

                # Whether the entity dropped or not, it is assumed that it did.
                entity.dropped = True
            elif not entity.dead:
                entity.process_ai(self, dt)
                entity.update(dt)

            # Collision between the player and entities in the room.
            if (
                not entity.dead
                and self.player.collides(entity)
                and not self.player.invulnerable
            ):
                settings.SOUNDS["hit-player"].play()
                self.player.damage(1)
                self.player.go_invulnerable(1.5)

                if self.player.health == 0:
                    self.on_game_over()

        self.entities = [entity for entity in self.entities if not entity.dead]

        for obj in list(self.objects):
            obj.update(dt)

            if self.player.collides(obj):
                obj.on_collide()

                if obj.solid and not obj.taken:
                    self._push_player_out_of(obj)

                if obj.consumable:
                    obj.on_consume(self.player, obj)
                    self.objects.remove(obj)

        for projectile in list(self.projectiles):
            projectile.update(dt)

            for entity in self.entities:
                if projectile.dead:
                    break

                if not entity.dead and projectile.collides(entity):
                    entity.damage(1)
                    settings.SOUNDS["hit-enemy"].play()
                    projectile.dead = True

            if projectile.dead:
                self.projectiles.remove(projectile)

    def _push_player_out_of(self, obj: GameObject) -> None:
        player = self.player
        player_y = player.y + player.height / 2
        player_height = player.height - player.height / 2
        player_right = player.x + player.width
        player_bottom = player_y + player_height

        if (
            player.direction == "left"
            and not (player_y >= (obj.y + obj.height))
            and not (player_bottom <= obj.y)
        ):
            player.x = obj.x + obj.width
        elif (
            player.direction == "right"
            and not (player_y >= (obj.y + obj.height))
            and not (player_bottom <= obj.y)
        ):
            player.x = obj.x - player.width
        elif (
            player.direction == "down"
            and not (player.x >= (obj.x + obj.width))
            and not (player_right <= obj.x)
        ):
            player.y = obj.y - player.height
        elif (
            player.direction == "up"
            and not (player.x >= (obj.x + obj.width))
            and not (player_right <= obj.x)
        ):
            player.y = obj.y + obj.height - player.height / 2

    def take_adjacent_pot(self, player: TypeVar("Player")) -> None:
        """
        Looks for a takeable object directly in front of the player (one
        tile away, in the direction they're currently facing) and, if
        found, removes it from the room and has the player lift it.
        """
        player_y = player.y + player.height / 2
        player_height = player.height - player.height / 2
        player_col = int((player.x + player.width / 2) // settings.TILE_SIZE)
        player_row = int((player_y + player_height / 2) // settings.TILE_SIZE)

        for obj in self.objects:
            if not obj.takeable:
                continue

            obj_col = int((obj.x + obj.width / 2) // settings.TILE_SIZE)
            obj_row = int((obj.y + obj.height / 2) // settings.TILE_SIZE)

            adjacent = (
                (player.direction == "right" and obj_row == player_row and obj_col == player_col + 1)
                or (player.direction == "left" and obj_row == player_row and obj_col == player_col - 1)
                or (player.direction == "up" and obj_col == player_col and obj_row == player_row - 1)
                or (player.direction == "down" and obj_col == player_col and obj_row == player_row + 1)
            )

            if adjacent:
                self.objects.remove(obj)
                player.change_state("pot-lift", pot=obj)
                return

    def _generate_walls_and_floors(self) -> None:
        """
        Generates the walls and floors of the room, randomizing the various
        varieties of said tiles for visual variety.
        """
        for y in range(1, self.height + 1):
            row = []

            for x in range(1, self.width + 1):
                if x == 1 and y == 1:
                    tile_id = settings.TILE_TOP_LEFT_CORNER
                elif x == 1 and y == self.height:
                    tile_id = settings.TILE_BOTTOM_LEFT_CORNER
                elif x == self.width and y == 1:
                    tile_id = settings.TILE_TOP_RIGHT_CORNER
                elif x == self.width and y == self.height:
                    tile_id = settings.TILE_BOTTOM_RIGHT_CORNER
                elif x == 1:
                    tile_id = random.choice(settings.TILE_LEFT_WALLS)
                elif x == self.width:
                    tile_id = random.choice(settings.TILE_RIGHT_WALLS)
                elif y == 1:
                    tile_id = random.choice(settings.TILE_TOP_WALLS)
                elif y == self.height:
                    tile_id = random.choice(settings.TILE_BOTTOM_WALLS)
                else:
                    tile_id = random.choice(settings.TILE_FLOORS)

                row.append(tile_id)

            self.tiles.append(row)

    def _generate_entities(self) -> None:
        """Randomly creates an assortment of enemies for the player to fight."""
        for _ in range(10):
            enemy_type = random.choice(_ENEMY_TYPES)
            definition = ENTITY_DEFS[enemy_type]

            entity = Entity(
                x=random.randint(
                    settings.MAP_RENDER_OFFSET_X + settings.TILE_SIZE,
                    settings.VIRTUAL_WIDTH - settings.TILE_SIZE * 2 - 16,
                ),
                y=random.randint(
                    settings.MAP_RENDER_OFFSET_Y + settings.TILE_SIZE,
                    settings.MAP_HEIGHT * settings.TILE_SIZE
                    + settings.MAP_RENDER_OFFSET_Y
                    - settings.TILE_SIZE
                    - 16,
                ),
                width=16,
                height=16,
                walk_speed=definition.get("walk_speed", 20),
                health=1,
                animation_defs=definition["animations"],
                states={},
            )

            entity.state_machine.states = {
                "walk": lambda sm, e=entity: EntityWalkState(e, sm),
                "idle": lambda sm, e=entity: EntityIdleState(e, sm),
            }
            entity.change_state("walk")
            self.entities.append(entity)

    def _generate_objects(self) -> None:
        """Randomly creates an assortment of obstacles for the player to navigate around."""
        switch = GameObject(
            GAME_OBJECT_DEFS["switch"],
            random.randint(
                settings.MAP_RENDER_OFFSET_X + settings.TILE_SIZE,
                settings.VIRTUAL_WIDTH - settings.TILE_SIZE * 2 - 16,
            ),
            random.randint(
                settings.MAP_RENDER_OFFSET_Y + settings.TILE_SIZE,
                settings.MAP_HEIGHT * settings.TILE_SIZE
                + settings.MAP_RENDER_OFFSET_Y
                - settings.TILE_SIZE
                - 16,
            ),
        )
        self.objects.append(switch)

        def open_all_doors() -> None:
            if switch.state == "unpressed":
                switch.state = "pressed"

                for doorway in self.doorways:
                    doorway.open = True

                settings.SOUNDS["door"].play()

        switch.on_collide = open_all_doors

        for y in range(2, self.height):
            for x in range(2, self.width):
                if random.randint(1, 20) == 1:
                    self.objects.append(
                        GameObject(GAME_OBJECT_DEFS["pot"], x * 16, y * 16)
                    )

    def render(
        self,
        surface: pygame.Surface,
        camera_offset_x: float = 0,
        camera_offset_y: float = 0,
    ) -> None:
        offset_x = self.adjacent_offset_x + camera_offset_x
        offset_y = self.adjacent_offset_y + camera_offset_y

        for y in range(self.height):
            for x in range(self.width):
                tile_id = self.tiles[y][x]
                surface.blit(
                    settings.TEXTURES["tiles"],
                    (
                        x * settings.TILE_SIZE + self.render_offset_x + offset_x,
                        y * settings.TILE_SIZE + self.render_offset_y + offset_y,
                    ),
                    settings.frame("tiles", tile_id),
                )

        for doorway in self.doorways:
            doorway.render(surface, offset_x, offset_y)

        for obj in self.objects:
            obj.render(surface, offset_x, offset_y)

        for entity in self.entities:
            if not entity.dead:
                entity.render(surface, offset_x, offset_y)

        # The player and projectiles are drawn using only the camera pan —
        # never this room's own adjacent_offset — matching the original,
        # where Player:render()/Projectile:render() take no room offset at
        # all. Their x/y already track the correct absolute (pre-camera-pan)
        # screen position on their own, including mid-tween during a room
        # shift; adding adjacent_offset on top (as tiles/entities do) would
        # draw them a full room-width off from where they actually are.
        #
        # Also masks them out entirely while within a door archway's
        # threshold — a plain rect-overlap stand-in for the original's
        # stencil test, which cut the same archway shape out of the player
        # draw so walking (or, mid room-shift, tweening) through the wall
        # opening doesn't show them clipping through solid wall.
        if self.player and not _in_any_doorway_zone(self.player.get_collision_rect()):
            self.player.render(surface, camera_offset_x, camera_offset_y)

        for projectile in self.projectiles:
            if not _in_any_doorway_zone(projectile.get_collision_rect()):
                projectile.render(surface, camera_offset_x, camera_offset_y)
