# Flappy Bird with Pause State and Hard Mode

This project is a Flappy Bird clone built with Python, Pygame and Gale. The base gameplay follows the classic arcade loop: the player controls a bird that must avoid obstacles by jumping at the right time while gravity pulls it downward.

## Original game

Flappy Bird is a side-scrolling arcade game where the player keeps a bird in the air and tries to pass through the gaps between obstacles. The score increases each time the bird successfully goes through an obstacle pair.

This project keeps the original gameplay but adds a pause system and a more advanced challenge mode.

## Change implemented

The project adds three main improvements to the original game:

1. A pause state that stops the action without losing the current session state.
2. Two gameplay modes implemented with the Strategy pattern: Normal and Hard.
3. A ghost-like booster that temporarily lets the bird pass through obstacles and changes the music.

## Pause state

A dedicated `PauseState` was added to stop the game while preserving the current world, bird and score. The state can be entered and exited with the same pause key, allowing the player to resume the game from the exact same point.

## Gameplay modes

The game uses the Strategy pattern to switch behaviors dynamically:

### Normal mode

This keeps the original Flappy Bird experience intact.
- the bird only jumps upward
- obstacle generation follows the standard pattern
- the gameplay stays close to the original version

### Hard mode

Hard mode increases the difficulty by adding several changes:
- the bird can move horizontally using left and right keys
- obstacle spacing is no longer fixed and varies between pairs
- the vertical position of each obstacle set changes based on the previous one, avoiding impossible layouts
- some obstacles open and close their gap dynamically
- collisions with moving obstacles trigger a sound effect

## Ghost booster

A random booster appears in the world and can be collected by the bird. Once activated, it grants a temporary ghost effect that lets the bird pass through obstacles for a limited time. The visual state becomes translucent and the background music changes while the effect is active.

After the duration ends, the bird and the music return to normal.

## Controls

- Jump: mouse click or assigned jump input
- Pause / Resume: `P`
- Hard mode horizontal movement: left and right keys

## Project structure

- `main.py`: entry point of the game
- `settings.py`: configuration, textures, sound, fonts and input bindings
- `src/FlappyBird.py`: main game class and global game state machine
- `src/Bird.py`: bird movement and boost logic
- `src/World.py`: world scrolling, obstacle generation and booster logic
- `src/strategies/`: gameplay strategies for Normal and Hard modes
- `src/states/`: game states, including pause and playing states
- `assets/`: graphics, fonts and sound effects

## Running the project

```bash
cd 02-flappy_bird
python main.py
```