# Super Martian with Key-Goal Progression and Tiled Level Design

This project is a platformer built with Python, Pygame and Gale. The base gameplay follows the classic side-scrolling action formula: the player moves across a level, collects coins, avoids enemies and reaches a goal while jumping across platforms.

## Original game

Super Martian is a platformer in which the player controls a small character that moves through a side-scrolling stage, collects items and survives obstacles. The general structure includes horizontal movement, jumping, ladder interaction, enemy collisions, coins and a timer-based survival loop.

This version keeps that platformer foundation but expands it with a custom level progression system, Tiled-based map design and a special key-object objective that finishes the level under specific score conditions.

## Change implemented

The project introduces:

1. A custom Tiled-based level design with multiple map layers.
2. A special solid block that becomes active only after the score target is reached.
3. A key that spawns from that block and can be collected to finish the level.
4. A level-completion transition based on an iris-out effect.
5. A timer lock and score-based progression system that stops coin collection once the level is effectively completed.

## Tiled level system

The level is built using Tiled data, loaded through the Gale tilemap system. The map includes multiple layers used for platforms, decoration and special objects. The level logic is not hardcoded only in Python: the project reads map structure and object data from JSON tilemaps such as `level1.json` and `level2.json`.

This means the stage is not just a static scene; it is a data-driven level with platform layouts, item placement and game objects defined by the map itself.

## Score-gated key block

The level includes a special block that remains inactive until the player reaches a required score threshold. The target score is defined in the project settings for each level, and the logic is checked directly in the gameplay state.

When the score target is reached:
- the key block becomes active
- the block changes its visual state to a triggered version
- a sound cue plays to confirm that the level target was reached

## Key spawning and level completion

Once the score threshold is met, the player must hit the activated block from below. The block behaves as a solid object and the jump logic checks whether the player is moving upward and colliding with the underside of the block.

When that condition is met:
- the key spawns at the same position as the block
- the object appears as if it emerges from the block
- the key is then collected by the player

After the player picks up the key, the level starts a completion flow that stops normal gameplay and transitions to the next stage or the final screen.

## Level transition effect

The completion sequence uses a circular iris-out transition. The screen is darkened and a shrinking circular mask closes around the player, creating a cartoon-style finish effect. This is implemented in the gameplay state as a transition overlay and is used before the next level is loaded.

The transition is tied to the event of picking up the key, so the level ends only after the objective has actually been completed.

## Timer and score lock

- the timer is stopped when the player picks up the key and the completion sequence begins
- the player can no longer collect additional coins after the completion flow starts
- the completion sound is triggered to confirm that the objective has been achieved


## Extra gameplay systems observed in the implementation

Beyond the required objective system, the project also includes additional mechanics that are part of the final build:

- camera follow for the player
- flying creatures spawned at random intervals
- collectible coin types with different score values
- HUD showing score, timer and target information
- pause state support while the game is active
- death and reset flow when the player falls or collides with enemies

## Controls

- Move left / right: `A` / `D` or arrow keys
- Jump: `Space` or mouse click
- Move up / down on ladders: `W` / `S` or arrow keys
- Pause: `P`

## Project structure

- `main.py`: game entry point
- `settings.py`: input bindings, constants, score targets, level data and sound configuration
- `src/GameLevel.py`: tilemap loading, object processing and key/block logic
- `src/Player.py`: player movement, controls and score state
- `src/GameItem.py`: collectible item logic and consumption behavior
- `src/definitions/items.py`: coin and key definitions
- `src/states/game_states/PlayState.py`: main gameplay loop, score check, key block activation, key collection and level transition
- `src/Clock.py`: countdown timer logic
- `src/Creature.py` and `src/FlyingCreature.py`: enemy and flying enemy behavior
- `assets/tilemaps/`: Tiled level files
- `assets/graphics/` and `assets/sounds/`: art and audio assets

## Running the project

```bash
cd 05-super_martian
python main.py
```

