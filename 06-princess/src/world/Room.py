"""
ISPPV1 2026
Study Case: The Legend of the Princess (ARPG)

Author: Eugenio Montilla
eugeniorusso1411@gmail.com

This file contains the class Room.
"""

import random
from typing import Any, Callable, List, Optional, TypeVar

import pygame

from gale.tilemap import TileMap
from gale.timer import Timer

import settings
from src.Fireball import Fireball
from src.definitions.entity import ENTITY_DEFS
from src.definitions.game_objects import GAME_OBJECT_DEFS
from src.Entity import Entity
from src.GameObject import GameObject
from src.states.entity.EntityIdleState import EntityIdleState
from src.states.entity.EntityWalkState import EntityWalkState
from src.states.entity.boss.BossIdleState import BossIdleState
from src.states.entity.boss.BossAttackState import BossAttackState
from src.states.entity.boss.BossChaseState import BossChaseState
from src.world.Doorway import Doorway

_ENEMY_TYPES = ["skeleton", "slime", "bat", "ghost", "spider"]

_BOSS_ROOM_CHANCE = 5

_CHEST_SPAWN_CHANCE = 5

_DOORWAY_ZONES = {
    "left": pygame.Rect(
        -settings.TILE_SIZE - 6,
        settings.MAP_RENDER_OFFSET_Y + settings.MAP_HEIGHT // 2 * settings.TILE_SIZE - settings.TILE_SIZE * 2,
        settings.TILE_SIZE * 2 + 6,
        settings.TILE_SIZE * 3,
    ),
    "right": pygame.Rect(
        settings.MAP_RENDER_OFFSET_X + settings.MAP_WIDTH * settings.TILE_SIZE - 6,
        settings.MAP_RENDER_OFFSET_Y + settings.MAP_HEIGHT // 2 * settings.TILE_SIZE - settings.TILE_SIZE * 2,
        settings.TILE_SIZE * 2 + 6,
        settings.TILE_SIZE * 3,
    ),
    "top": pygame.Rect(
        settings.MAP_RENDER_OFFSET_X + settings.MAP_WIDTH // 2 * settings.TILE_SIZE - settings.TILE_SIZE,
        -settings.TILE_SIZE - 6,
        settings.TILE_SIZE * 2,
        settings.TILE_SIZE * 2 + 12,
    ),
    "bottom": pygame.Rect(
        settings.MAP_RENDER_OFFSET_X + settings.MAP_WIDTH // 2 * settings.TILE_SIZE - settings.TILE_SIZE,
        settings.VIRTUAL_HEIGHT - settings.TILE_SIZE - 6,
        settings.TILE_SIZE * 2,
        settings.TILE_SIZE * 2 + 12,
    ),
}


def _doorway_opening_for(
    rect: pygame.Rect, doorways_by_direction: dict
) -> pygame.Rect | None:
    for direction, zone in _DOORWAY_ZONES.items():
        if rect.colliderect(zone):
            doorway = doorways_by_direction.get(direction)
            if doorway is not None:
                return doorway.get_collision_rect()
    return None


class Room:
    def __init__(
        self,
        player: TypeVar("Player"),
        on_game_over: Callable[[], None],
        is_boss_room: bool = False,
        entry_direction: Optional[str] = None,
        spawn_chest: bool = False,
    ) -> None:
        self.player = player
        self.on_game_over = on_game_over

        self.is_boss_room = is_boss_room
        self.entry_direction = entry_direction

        self.width = settings.MAP_WIDTH
        self.height = settings.MAP_HEIGHT

        self.tilemap = TileMap(settings.TILE_SIZE, settings.TILE_SIZE, self.width, self.height)
        self.tilemap.add_tileset(settings.TILESET)
        self._generate_walls_and_floors()

        self.entities: List[Entity] = []

        self.objects: List[GameObject] = []
        self._chest: Optional[GameObject] = None

        if is_boss_room:
            boss_direction = "right"
            if entry_direction:
                _opposite = {"left": "right", "right": "left", "up": "down", "down": "up"}
                boss_direction = _opposite.get(entry_direction, "right")
            self._generate_boss(boss_direction)
        else:
            self._generate_entities()
            self._generate_objects(spawn_chest=spawn_chest)

        self._boss: Optional[Entity] = self.entities[0] if is_boss_room and self.entities else None
        self._boss_immune = True
        self._boss_vuln_timer = 0.0
        _BOSS_VULN_DURATION = 3.0
        self._boss_vuln_duration = _BOSS_VULN_DURATION

        # Doorways that lead to other dungeon rooms.
        self.doorways = []
        if is_boss_room and entry_direction:
            self._entry_doorway_dir = entry_direction
            self.doorways.append(Doorway(self._entry_doorway_dir, False, self))
        else:
            self.doorways = [
                Doorway("top", False, self),
                Doorway("bottom", False, self),
                Doorway("left", False, self),
                Doorway("right", False, self),
            ]

        self._doorways_by_direction = {
            doorway.direction: doorway for doorway in self.doorways
        }

        self.render_offset_x = settings.MAP_RENDER_OFFSET_X
        self.render_offset_y = settings.MAP_RENDER_OFFSET_Y

        self.adjacent_offset_x = 0
        self.adjacent_offset_y = 0
        self._boss_vuln_timer = 0.0

        self.projectiles: List[Any] = []

    def update(self, dt: float) -> None:
        if self.adjacent_offset_x != 0 or self.adjacent_offset_y != 0:
            return

        self.player.update(dt)

        if self.is_boss_room and not self._boss_immune:
            self._boss_vuln_timer -= dt
            if self._boss_vuln_timer <= 0:
                self._boss_immune = True

        for entity in self.entities:
            if entity.health <= 0:
                entity.dead = True
                if self.is_boss_room:
                    for doorway in self.doorways:
                        doorway.open = True
                    settings.SOUNDS["door"].play()
                else:
                    if not entity.dropped and random.randint(1, 10) == 1:
                        self.objects.append(
                            GameObject(GAME_OBJECT_DEFS["heart"], entity.x, entity.y)
                        )
                entity.dropped = True
            elif not entity.dead:
                entity.process_ai(self, dt)
                entity.update(dt)

            if (
                not entity.dead
                and self.player.collides(entity)
                and not self.player.invulnerable
            ):
                settings.SOUNDS["hit-player"].play()
                if self.is_boss_room:
                    self.player.damage(2)
                else:
                    self.player.damage(1)
                self.player.go_invulnerable(1.5)

                if self.player.health <= 0:
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

            if projectile.dead:
                self.projectiles.remove(projectile)
                continue

            if getattr(projectile.obj, "is_arrow", False) or type(projectile.obj).__name__ == "Arrow":
                if self.is_boss_room and self._boss and not self._boss.dead:
                    if projectile.collides(self._boss):
                        self._boss_immune = False  
                        self._boss_vuln_timer = 3.0
                        settings.SOUNDS["boss-hit"].play()
                        projectile.dead = True
                        if projectile in self.projectiles:
                            self.projectiles.remove(projectile)
                        continue

                for entity in list(self.entities):
                    if not entity.dead and projectile.collides(entity):
                        entity.damage(1)
                        settings.SOUNDS["hit-enemy"].play()
                        projectile.dead = True
                        if projectile in self.projectiles:
                            self.projectiles.remove(projectile)
                        break

            elif type(projectile.obj).__name__ == "Fireball":
                if not self.player.invulnerable and projectile.collides(self.player):
                    projectile.obj.hit_player()
                    if projectile in self.projectiles:
                        self.projectiles.remove(projectile)

            else:
                for entity in list(self.entities):
                    if projectile.dead:
                        break
                    if not entity.dead and projectile.collides(entity):
                        entity.damage(1)
                        settings.SOUNDS["hit-enemy"].play()
                        projectile.dead = True

                if projectile.dead and projectile in self.projectiles:
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

    def _is_player_adjacent(self, player: TypeVar("Player"), obj_x: float, obj_y: float, obj_width: float, obj_height: float) -> bool:
        player_y = player.y + player.height / 2
        player_height = player.height - player.height / 2
        player_col = int((player.x + player.width / 2) // settings.TILE_SIZE)
        player_row = int((player_y + player_height / 2) // settings.TILE_SIZE)
        
        obj_col = int((obj_x + obj_width / 2) // settings.TILE_SIZE)
        obj_row = int((obj_y + obj_height / 2) // settings.TILE_SIZE)

        return (
            (player.direction == "right" and obj_row == player_row and obj_col == player_col + 1)
            or (player.direction == "left" and obj_row == player_row and obj_col == player_col - 1)
            or (player.direction == "up" and obj_col == player_col and obj_row == player_row - 1)
            or (player.direction == "down" and obj_col == player_col and obj_row == player_row + 1)
        )

    def take_adjacent_pot(self, player: TypeVar("Player")) -> None:
        """
        Looks for a takeable object directly in front of the player (one
        tile away, in the direction they're currently facing) and, if
        found, removes it from the room and has the player lift it.
        """
        for obj in self.objects:
            if not obj.takeable:
                continue

            if self._is_player_adjacent(player, obj.x, obj.y, obj.width, obj.height):
                self.objects.remove(obj)
                player.change_state("pot-lift", pot=obj)
                return

    def _generate_walls_and_floors(self) -> None:
        """
        Generates the walls and floors of the room, randomizing the various
        varieties of said tiles for visual variety.
        """
        floor = self.tilemap.add_layer("floor")

        for y in range(1, self.height + 1):
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

                floor[y - 1][x - 1] = tile_id

    def _generate_entities(self) -> None:
        """Randomly creates an assortment of enemies for the player to fight."""
        for _ in range(10):
            enemy_type = random.choice(_ENEMY_TYPES)
            definition = ENTITY_DEFS[enemy_type]
            
            safe_x, safe_y = self._get_safe_spawn_position(16, 16)
            
            entity = Entity(
                x=safe_x,
                y=safe_y,
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

    def _generate_objects(self, spawn_chest: bool = False) -> None:
        """Randomly creates an assortment of obstacles for the player to navigate around."""
        
        sx, sy = self._get_safe_spawn_position(16, 16)
        switch = GameObject(
            GAME_OBJECT_DEFS["switch"],
            sx,
            sy
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
                if abs(x - self.width // 2) <= 1 or abs(y - self.height // 2) <= 1:
                    continue
                    
                if random.randint(1, 20) == 1:
                    self.objects.append(
                        GameObject(GAME_OBJECT_DEFS["pot"], x * 16, y * 16)
                    )

        if spawn_chest:
            cx, cy = self._get_safe_spawn_position(16, 16)
            chest = GameObject(
                GAME_OBJECT_DEFS["chest"],
                cx,
                cy
            )
            self.objects.append(chest)
            self._chest = chest

    def _generate_boss(self, boss_direction: str = "right") -> None:
        definition = ENTITY_DEFS["boss"]
        
        bx = settings.VIRTUAL_WIDTH / 2 - 32
        by = settings.VIRTUAL_HEIGHT / 2 - 36
        
        if boss_direction == "right":
            bx = settings.MAP_RENDER_OFFSET_X + settings.MAP_WIDTH * settings.TILE_SIZE - settings.TILE_SIZE * 3
        elif boss_direction == "left":
            bx = settings.MAP_RENDER_OFFSET_X + settings.TILE_SIZE * 2
        elif boss_direction == "down":
            by = settings.MAP_RENDER_OFFSET_Y + settings.MAP_HEIGHT * settings.TILE_SIZE - settings.TILE_SIZE * 3
        elif boss_direction == "up":
            by = settings.MAP_RENDER_OFFSET_Y + settings.TILE_SIZE * 2

        boss = Entity(
            x=bx,
            y=by,
            width=32,
            height=32,
            walk_speed=definition.get("walk_speed", 40),
            health=definition.get("health", 6),
            animation_defs=definition["animations"],
            states={},
        )
        boss.offset_x = 16
        boss.offset_y = 40
        boss.state_machine.states = {
            "idle":   lambda sm, b=boss: BossIdleState(b, sm, self),
            "attack": lambda sm, b=boss: BossAttackState(b, sm, self),
            "walk":   lambda sm, b=boss: BossChaseState(b, sm, self),
        }
        boss.change_state("walk")  
        self.entities.append(boss)
        self._boss = boss

    def interact_with_chest(self, player: TypeVar("Player")) -> None:
        if not self._chest or self._chest.state == "open":
            return

        chest = self._chest

        if self._is_player_adjacent(player, chest.x, chest.y, chest.width, chest.height):
            chest.state = "open"
            player.receive_bow()
            
            bow_item = GameObject(GAME_OBJECT_DEFS["bow"], chest.x, chest.y)
            self.objects.append(bow_item)
            Timer.tween(
                0.5,
                [(bow_item, {"y": chest.y - 16})],
                on_finish=lambda: self.objects.remove(bow_item) if bow_item in self.objects else None
            )

    def _get_safe_spawn_position(self, obj_width: float, obj_height: float) -> tuple[float, float]:
        safe_margin = settings.TILE_SIZE * 3
        center_rect = pygame.Rect(
            settings.VIRTUAL_WIDTH // 2 - safe_margin,
            settings.VIRTUAL_HEIGHT // 2 - safe_margin,
            safe_margin * 2, 
            safe_margin * 2
        )

        while True:
            x = random.randint(
                settings.MAP_RENDER_OFFSET_X + settings.TILE_SIZE,
                settings.VIRTUAL_WIDTH - settings.TILE_SIZE * 2 - int(obj_width),
            )
            y = random.randint(
                settings.MAP_RENDER_OFFSET_Y + settings.TILE_SIZE,
                settings.MAP_HEIGHT * settings.TILE_SIZE + settings.MAP_RENDER_OFFSET_Y - settings.TILE_SIZE - int(obj_height),
            )
            test_rect = pygame.Rect(x, y, obj_width, obj_height)

            if test_rect.colliderect(center_rect):
                continue
                
            blocked = False
            for zone in _DOORWAY_ZONES.values():
                if test_rect.colliderect(zone):
                    blocked = True
                    break
            
            if not blocked:
                return x, y

    def render(
        self,
        surface: pygame.Surface,
        camera_offset_x: float = 0,
        camera_offset_y: float = 0,
    ) -> None:
        offset_x = self.adjacent_offset_x + camera_offset_x
        offset_y = self.adjacent_offset_y + camera_offset_y

        # Surface.subsurface() (used for 07-ultimate_fantasy's BattleState,
        for y in range(self.height):
            for x in range(self.width):
                gid = self.tilemap.get_gid("floor", y, x)
                tileset = self.tilemap.tileset_for_gid(gid)
                surface.blit(
                    tileset.image,
                    (
                        x * settings.TILE_SIZE + self.render_offset_x + offset_x,
                        y * settings.TILE_SIZE + self.render_offset_y + offset_y,
                    ),
                    tileset.rect_for(gid),
                )

        for doorway in self.doorways:
            doorway.render(surface, offset_x, offset_y)

        for obj in self.objects:
            obj.render(surface, offset_x, offset_y)

        for entity in self.entities:
            if not entity.dead:
                entity.render(surface, offset_x, offset_y)
                
                if self.is_boss_room and entity == self._boss:
                    bar_w = 32
                    bar_h = 4
                    bx = entity.x + offset_x + entity.width / 2 - bar_w / 2
                    by = entity.y + offset_y - entity.offset_y - 8
                    
                    # Draw name
                    font = settings.FONTS["tiny"]
                    text_surf = font.render("The Reaper", True, (255, 255, 255))
                    tx = entity.x + offset_x + entity.width / 2 - text_surf.get_width() / 2
                    ty = by - text_surf.get_height() - 2
                    surface.blit(text_surf, (tx, ty))
                    
                    pygame.draw.rect(surface, (255, 0, 0), (bx, by, bar_w, bar_h))
                    health_ratio = max(0.0, entity.health / 6.0)
                    health_w = int(health_ratio * bar_w)
                    if health_w > 0:
                        bar_color = (0, 255, 0) if self._boss_immune else (255, 255, 0)
                        pygame.draw.rect(surface, bar_color, (bx, by, health_w, bar_h))

        #
        if self.player:
            self.player.visibility_clip_rect = _doorway_opening_for(
                self.player.get_collision_rect(), self._doorways_by_direction
            )
            self.player.render(surface, camera_offset_x, camera_offset_y)
            self.player.visibility_clip_rect = None

        for projectile in self.projectiles:
            if not _doorway_opening_for(
                projectile.get_collision_rect(), self._doorways_by_direction
            ):
                projectile.render(surface, camera_offset_x, camera_offset_y)
