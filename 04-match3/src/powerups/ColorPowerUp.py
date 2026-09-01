from __future__ import annotations

from typing import Any, List

import settings

from .PowerUp import BasePowerUp


class ColorPowerUp(BasePowerUp):
    kind = "color"

    def targets(self, board: Any, tile: Any = None) -> List[Any]:
        target_tile = tile if tile is not None else self.tile
        targets: List[Any] = []
        for i in range(settings.BOARD_HEIGHT):
            for j in range(settings.BOARD_WIDTH):
                candidate = board.tiles[i][j]
                if candidate is not None and candidate.color == target_tile.color:
                    targets.append(candidate)
        return targets
