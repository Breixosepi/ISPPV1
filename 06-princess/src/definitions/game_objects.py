"""
ISPPV1 2026
Study Case: The Legend of the Princess (ARPG)

Author: Eugenio Montilla
eugeniorusso1411@gmail.com

This file contains the definition for game objects.
"""

from typing import Any, Dict

import settings


def _pickup_heart(player, obj) -> None:
    player.heal(2)
    settings.SOUNDS["heart-taken"].play()


GAME_OBJECT_DEFS: Dict[str, Dict[str, Any]] = {
    "switch": {
        "type": "switch",
        "texture": "switches",
        "frame": 2,
        "width": 16,
        "height": 16,
        "solid": False,
        "default_state": "unpressed",
        "states": {
            "unpressed": {"frame": 2},
            "pressed": {"frame": 1},
        },
    },
    "pot": {
        "type": "pot",
        "texture": "tiles",
        "frame": 16,
        "width": 16,
        "height": 16,
        "solid": True,
        "consumable": False,
        "default_state": "default",
        "takeable": True,
        "states": {
            "default": {"frame": 16},
        },
    },
    "heart": {
        "type": "heart",
        "texture": "hearts",
        "frame": 5,
        "width": 16,
        "height": 16,
        "solid": False,
        "consumable": True,
        "default_state": "default",
        "states": {
            "default": {"frame": 5},
        },
        "on_consume": _pickup_heart,
    },
    # ─────────────────────────────────────────────────────────────────────────
    "chest": {
        "type": "chest",
        "texture": "chest",
        "frame": 1,
        "width": 16,
        "height": 16,
        "solid": True,
        "consumable": False,
        "takeable": False,
        "default_state": "closed",
        "states": {
            "closed": {"frame": 1},
            "open":   {"frame": 2},
        },
    },

    "arrow": {
        "type": "arrow",
        "texture": "arrow",
        "frame": 1,
        "width": 16,
        "height": 16,
        "solid": False,
        "consumable": False,
        "takeable": False,
        "default_state": "idle",
        "states": {
            "idle": {"frame": 1},
        },
    },
    
    "bow": {
        "type": "bow",
        "texture": "bow",
        "frame": 1,
        "width": 16,
        "height": 16,
        "solid": False,
        "consumable": False,
        "takeable": False,
        "default_state": "idle",
        "states": {
            "idle": {"frame": 1},
        },
    },
}
