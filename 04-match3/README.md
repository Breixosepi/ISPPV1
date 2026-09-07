# Match-3 with Drag-and-Drop, Board Rebuild and Power-Ups

This project is a Match-3 puzzle game built with Python, Pygame and Gale. The base gameplay follows the classic board-based loop: the player swaps adjacent tiles, forms matches of three or more, clears them and continues until the board is solved or the level objective is met.

## Original game

Match-3 games are tile-based puzzle games where the player rearranges pieces on a grid to create groups of identical tiles. A valid match is usually formed by three or more tiles aligned horizontally or vertically, after which they are removed and replaced by falling pieces.

This project keeps the original Match-3 structure but adds several refinements that increase control, clarity and tactical depth.

## Change implemented

The main additions in this version are:

1. Drag-and-drop tile movement instead of simple click selection.
2. Valid-move feedback with a green/red highlight during drag.
3. Automatic board rebuild when no valid move exists.
4. Special power-ups created from 4-tile and 5+-tile matches.
5. Visual explosion effects for power-up activation and match resolution.

## Drag-and-drop interaction

The tile movement system was redesigned so the player drags a tile instead of selecting it with a single click. While the mouse button is held down, the tile stays attached to the pointer and follows its position over the board.

When the mouse is released, the tile is dropped. If the movement is valid and creates a legal match, the move is accepted. If not, the tile returns to its original spot.

During dragging, the game also displays a visual guide that helps the player decide whether a swap is legal:
- green highlight for a valid target
- red highlight for an invalid target

## Restriction on valid moves

Only moves that create a valid match are allowed. This prevents random or useless swaps and keeps the gameplay focused on meaningful decisions. The system checks whether a proposed swap would create a match before accepting the move.

## Automatic board rebuild

If no valid move exists at any point, the board is automatically recreated. After a move or match resolution, the game verifies whether a legal move is still available. If not, it regenerates the grid until there is at least one valid movement.

## Match and power-up visual feedback

The game includes animated particle explosions when tiles are removed as part of a match or when a power-up triggers. These effects are produced through a particle system that bursts around the destroyed tiles.


### Line Clear power-up (4 tiles)

A power-up is generated when exactly 4 tiles match. It appears in the position of the last moved tile and inherits the color of the matched tiles.

This power-up can be moved like a normal tile and can also be activated directly by clicking it. When triggered, it explodes and destroys all neighboring tiles in horizontal and vertical directions, acting like a line-clearing effect.

### Color Bomb power-up (5+ tiles)

A power-up is generated when 5 or more tiles match. It appears in the position of the last moved tile and inherits the color of the matched tiles.

This power-up can be moved or activated manually. When triggered, it explodes and destroys every tile of the same color present anywhere on the board.

## Controls

- Drag a tile with the mouse to move it.
- Release the mouse to drop the tile into a new position.
- Click a generated power-up to activate it when needed.
- Valid moves are highlighted in green; invalid targets are highlighted in red.

## Project structure

- `main.py`: entry point of the game
- `settings.py`: constants, colors and board configuration
- `src/Match3.py`: main gameplay controller
- `src/Board.py`: board logic, matching, move validation, rebuild flow and power-up creation
- `src/Tile.py`: tile definition, rendering and power-up visual treatment
- `src/powerups/`: line clear and color bomb power-ups
- `src/states/`: gameplay states and board flow
- `assets/`: graphical resources and visual assets

## Running the project

```bash
cd 04-match3
python main.py
```

