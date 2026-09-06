"""
ISPPV1 2026
Study Case: The Legend of the Princess (ARPG)

Author: Eugenio Montilla
eugeniorusso1411@gmail.com
Bow - Factory pattern for Arrow projectiles.
"""
from typing import TYPE_CHECKING
from src.Projectile import Projectile
import settings
from src.GameObject import GameObject
from src.definitions.game_objects import GAME_OBJECT_DEFS
if TYPE_CHECKING:
    from src.Player import Player


class Bow:
    @staticmethod
    def fire(player: "Player") -> Projectile:
        direction = player.direction
        aw = 16
        ah = 16
        if direction == "right":
            x = player.x + player.width
            y = player.y + player.height / 2 - ah / 2
        elif direction == "left":
            x = player.x - aw
            y = player.y + player.height / 2 - ah / 2
        elif direction == "up":
            x = player.x + player.width / 2 - aw / 2
            y = player.y - ah
        else:
            x = player.x + player.width / 2 - aw / 2
            y = player.y + player.height
        
        arrow_obj = GameObject(GAME_OBJECT_DEFS["arrow"], x, y)
        arrow_obj.is_arrow = True 
        
        return Projectile(arrow_obj, direction, speed=220)
