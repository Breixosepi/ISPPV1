"""
ISPPV1 2026
Study Case: Super Martian (Platformer)

Author: Eugenio Montilla
eugeniorusso1411@gmail.com

This file contains the definition for items.
"""

from typing import Dict, Any

import random

from gale.timer import Timer

import settings
from src.GameItem import GameItem
from src.Player import Player


def pickup_coin(
    coin: GameItem, player: Player, points: int, color: int, time: float
) -> None:
    settings.SOUNDS["pickup_coin"].stop()
    settings.SOUNDS["pickup_coin"].play()
    player.score += points
    player.coins_counter[color] += 1
    Timer.after(time, lambda: coin.respawn())


def pickup_green_coin(coin: GameItem, player: Player):
    pickup_coin(coin, player, 1, settings.COIN_GREEN, random.uniform(2, 4))


def pickup_blue_coin(coin: GameItem, player: Player):
    pickup_coin(coin, player, 5, settings.COIN_BLUE, random.uniform(5, 8))


def pickup_red_coin(coin: GameItem, player: Player):
    pickup_coin(coin, player, 20, settings.COIN_RED, random.uniform(10, 18))


def pickup_yellow_coin(coin: GameItem, player: Player):
    pickup_coin(coin, player, 50, settings.COIN_YELLOW, random.uniform(20, 25))


def pickup_key(key: GameItem, player: Player):
    """Picking up the key marks the level as completed."""
    settings.SOUNDS["level_complete"].stop()
    settings.SOUNDS["level_complete"].play()
    player.has_key = True


ITEMS: Dict[str, Dict[int, Dict[str, Any]]] = {
    "coins": {
        settings.COIN_GREEN: {
            "texture_id": "tiles",
            "consumable": True,
            "collidable": True,
            "on_consume": pickup_green_coin,
        },
        settings.COIN_BLUE: {
            "texture_id": "tiles",
            "consumable": True,
            "collidable": True,
            "on_consume": pickup_blue_coin,
        },
        settings.COIN_RED: {
            "texture_id": "tiles",
            "consumable": True,
            "collidable": True,
            "on_consume": pickup_red_coin,
        },
        settings.COIN_YELLOW: {
            "texture_id": "tiles",
            "consumable": True,
            "collidable": True,
            "on_consume": pickup_yellow_coin,
        },
    },
    "key": {
        settings.KEY_FRAME_INDEX: {
            "texture_id": "dungeon_tiles",
            "consumable": True,
            "collidable": True,
            "on_consume": pickup_key,
        },
    },
}
