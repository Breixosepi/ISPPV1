# Ultimate Fantasy with Active Time Battle (ATB) and Out-of-Combat Skills

This project is a classic Japanese-style Role-Playing Game (JRPG) built with Python, Pygame, and Gale. The gameplay follows the traditional loop of exploring an overworld, triggering random encounters, fighting enemies in turn-based combat, gaining experience, and leveling up characters.

## Original game

The original concept is heavily inspired by early 8-bit and 16-bit era RPGs. The player controls a party of characters exploring a procedurally generated tile-based overworld. The core mechanics include map traversal, random enemy encounters, turn-based combat using a sequential round system, leveling up through experience points, and increasing character stats. The game uses a state machine to manage the transition between overworld exploration, menus, and the battle screen.

This project preserves the overworld exploration and character progression mechanics but completely overhauls the battle system and expands the menu functionality.

## Change implemented

The main delivered enhancements are the addition of out-of-combat skill usage and the implementation of an Active Time Battle (ATB) system:

1. A detailed party status GUI that displays individual character stats (Level, HP, EXP, Attack, Defense, Magic).
2. The ability to use healing skills outside of combat through the pause menu.
3. Action visualization using transparency (alpha values) to distinguish between usable (healing) and disabled (offensive) skills in the pause menu.
4. A cooldown-based Active Time Battle (ATB) system that replaces the traditional static turn rounds.
5. An ATB progress bar in the combat GUI to visualize turn readiness.
6. Integration of the "Run" option directly into the individual character action menus.

## Detailed party status and out-of-combat healing

The pause menu has been expanded. When the player pauses the game during overworld exploration, the `PartyStatusView` is displayed with a new detail panel. The player can navigate through the party members to view their specific stats (Level, EXP, HP, Attack, Defense, and Magic).

Additionally, the player can access a skills menu. While offensive skills are displayed with partial transparency (alpha value) to indicate they cannot be used, healing skills are fully opaque. The player can select individual healing spells to restore HP to a specific party member, or use global healing spells to restore HP to the entire party, executing the same exact logic as during combat.

## Active Time Battle (ATB) system

The traditional sequential round-based combat has been replaced with a dynamic, time-based system. Each battle entity (party members and enemies) now has an action-specific cooldown timer (`wait_time`).

When the battle starts, these timers begin to tick down in real-time. The combat state continuously updates the timers of all entities. The first entity whose timer reaches zero earns the right to take a turn and is placed in a queue.

This creates a more organic flow where faster characters or those who use lighter actions will act more frequently than slow characters or those casting powerful magic.

## ATB visual progress and action selection

To communicate the ATB system to the player, a yellow progress bar has been added below the health bar of each party member in the `PartyStatusView` during combat. This bar fills up as the character's cooldown timer ticks down. Once the bar is full, the character's turn begins.

Because the combat is now character-driven rather than round-driven, the generic "Fight/Run" menu at the start of each round was removed. The "Run" option has been moved to the individual character's action menu, alongside their specific skills and the "Nothing" (skip turn) option.

## Controls

- Move: Arrow keys
- Confirm / Interact: `Enter`
- Pause / Open Menu: `P`
- Go Back / Cancel in menus: selecting Back in the UI
- Quit: `Escape` (from the main overworld)

## Project structure

- `main.py`: entry point of the game
- `settings.py`: constants, input bindings, fonts, sounds, and music
- `src/UltimateFantasy.py`: game bootstrap and main state machine
- `src/definitions/entity.py`: character classes, enemy definitions, and action dictionaries (including ATB wait times)
- `src/entity/BattleEntity.py`: base class for combat entities, managing HP, stats, and ATB cooldowns
- `src/states/game/BattleState.py`: main combat loop, ATB timer management, and turn queue logic
- `src/states/game/TakeTurnState.py`: individual entity turn execution and combat resolution
- `src/states/game/PauseSkillsState.py`: out-of-combat skill selection and alpha transparency logic
- `src/gui/PartyStatusView.py`: GUI component rendering character stats, health bars, and ATB gauges
- `src/gui/AlphaMenu.py`: UI component for rendering text lists with varying transparency
- `src/world/`: overworld generation and tile management
- `assets/`: sprites, music, and sound effects

## Running the project

```bash
cd 07-ultimate_fantasy
python main.py
```

