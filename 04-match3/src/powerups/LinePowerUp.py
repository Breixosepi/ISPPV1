from __future__ import annotations

from typing import Any, List

import settings

from .PowerUp import BasePowerUp


class LinePowerUp(BasePowerUp):
    kind = "line"

    def targets(self, board: Any, tile: Any = None) -> List[Any]:
        target_tile = tile if tile is not None else self.tile
        targets: List[Any] = []
        for j in range(settings.BOARD_WIDTH):
            candidate = board.tiles[target_tile.i][j]
            if candidate is not None:
                targets.append(candidate)
        for i in range(settings.BOARD_HEIGHT):
            candidate = board.tiles[i][target_tile.j]
            if candidate is not None:
                targets.append(candidate)
        return list(dict.fromkeys(targets))
