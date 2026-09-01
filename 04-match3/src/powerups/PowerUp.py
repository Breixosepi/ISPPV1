from __future__ import annotations

from typing import Any, List


class BasePowerUp:
    kind = "base"

    def __init__(self, x: int = 0, y: int = 0, **properties: Any) -> None:
        self.x = x
        self.y = y
        self.tile = properties.get("tile")

    def targets(self, board: Any, tile: Any = None) -> List[Any]:
        raise NotImplementedError

    def apply(self, board: Any, tile: Any = None) -> List[Any]:
        target_tile = tile if tile is not None else self.tile
        return self.targets(board, target_tile)
