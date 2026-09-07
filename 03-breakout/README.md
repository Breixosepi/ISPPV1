# Breakout with Capture, Cannon and Fireball Power-Ups

This project is a classic Breakout game built with Python, Pygame and Gale. The original gameplay follows the standard arcade formula: the player moves a paddle at the bottom of the screen, keeps a ball in play and destroys bricks by hitting them.

## Original game

Breakout is a brick-breaking arcade game where the player controls a paddle and tries to eliminate every brick on the board. The round ends when the player clears the level or when the ball falls past the paddle.

This version keeps the base mechanics of the original game and adds several special power-ups that expand the gameplay and create new tactical options.

## Change implemented

The project adds three main power-ups to the classic Breakout experience:

1. Ball capture power-up
2. Cannon power-up
3. Fireball power-up

These effects change how the player interacts with the ball, the paddle and the brick layout while preserving the original identity of the game.

## Ball-capture power-up

The ball-capture power-up lets the player catch the ball after it hits the paddle. Instead of bouncing immediately, the ball remains attached to the paddle at the impact point.

While the ball is attached:
- the player can move the paddle freely
- the ball stays stuck to the paddle
- pressing the space bar releases the ball again

This creates a more controlled moment and makes the next shot easier to aim.

## Cannon power-up

The cannon power-up adds two cannons mounted on the left and right ends of the paddle. When activated, they fire vertical projectiles simultaneously toward the brick wall.

The cannon effect gives the player an alternate way to destroy bricks without relying only on the ball. Only one active pair of cannon projectiles can exist at a time.

## Fireball power-up

The third power-up adds a fireball effect to the active balls. When collected, the ball visuals change to a blazing fireball style and the effect lasts for a limited time.

The key mechanic of this power-up is that, while the fireball effect is active, the ball can destroy bricks regardless of their tier or strength. In other words, it ignores the normal resistance system of the brick structure and breaks through blocks without being limited by their level or durability.

## Controls

- Move paddle: left and right arrows / `A` and `D`
- Launch the caught ball: `Space`
- Fire cannons: `F`

## Project structure

- `main.py`: entry point of the game
- `settings.py`: constants, textures, sounds and input mappings
- `src/Breakout.py`: main game logic and state management
- `src/Paddle.py`: paddle movement and interaction with power-ups
- `src/Ball.py`: ball motion and collision rules
- `src/Brick.py` and `src/BrickSet.py`: brick behavior and board logic
- `src/powerups/`: capture, cannon, fireball and other power-up classes
- `src/controllers/`: logic for the active power-up effects
- `src/states/`: starting, serving, playing and end-game states
- `assets/`: graphics, fonts and sound effects

## Running the project

```bash
cd 03-breakout
python main.py
```
