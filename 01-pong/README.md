# Pong with AI-Controlled Paddle

This project is a classic implementation of Pong built with Python, Pygame and Gale. The base gameplay follows the traditional arcade version: two paddles, one ball, score tracking and a state-based game flow.

## Original game

Pong is a two-player arcade game where each player controls a vertical paddle and tries to prevent the ball from passing behind them. The objective is to return the ball and make the opponent miss.

In the standard version, both paddles are controlled by keyboard input. This project modifies that behavior by assigning one paddle to an AI-controlled opponent.

## Change implemented

One of the paddles is now controlled by artificial intelligence. The AI follows the ball along the Y axis and moves the paddle to intercept it. This keeps the gameplay faithful to the original Pong experience while adding a playable automated opponent.

The human player controls the remaining paddle, while the AI paddle plays automatically.

## Controls

- Player paddle: `W` / `S`
- AI paddle: automatic

If the project is configured with the opposite side controlled by the player, the same principle applies: one paddle is human-controlled and the other is AI-controlled.

## Project structure

- `main.py`: entry point of the game
- `settings.py`: game constants, display settings and input configuration
- `src/Pong.py`: main game logic
- `src/Paddle.py`: paddle behavior, including AI movement
- `src/Ball.py`: ball physics and collisions
- `src/states/`: game states such as title, serve, gameplay and end states

## Running the project

```bash
cd 01-pong
python main.py
```
