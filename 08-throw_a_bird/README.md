# Throw a Bird with Split Ability and Dynamic Camera

This project is a physics-based puzzle game built with Python, Pygame, and Gale. The gameplay follows the traditional loop of aiming, flinging a projectile from a slingshot, and destroying structures built with rigid bodies to defeat enemies.

## Original game

The original concept is a continuous physics sandbox. The player drags and releases a heavy, invulnerable bird to launch it across a level against a tower made of stone, wood, and alien blocks. The core mechanics include map panning, dynamic zoom, physical impacts that calculate structural damage based on speed and mass, and a victory condition triggered when all enemies are destroyed.

## Change implemented

The main delivered enhancements are the addition of a mid-air split ability, strict collision rules, and a dynamic camera system:

1. A centralized `BirdManager` to handle the lifecycle and rendering of multiple birds simultaneously.
2. A split ability activated via the spacebar that divides the main bird into three separate projectiles mid-flight.
3. Angle-based velocity calculations to spread the cloned birds preserving their original momentum.
4. A strict, discrete collision detection system that disables the split ability permanently upon the first impact.
5. A group-based idle detection system to ensure the turn only ends when all active birds come to a complete stop.
6. A dynamic camera focus feature allowing the player to cycle observation between the split birds via mouse clicks.

## Bird split ability and manager

A new `BirdManager` class was introduced to encapsulate the spawning, tracking, and destruction of the projectiles. When the player presses the spacebar while the bird is in flight, the manager reads the current velocity vector of the primary bird. 

Using vector math, it instantiates two new identical clones at the exact same position, rotating their velocity vectors by 20 degrees upwards and downwards. This creates a natural spread effect, allowing the player to hit multiple weak points in the tower simultaneously. 

## First-impact collision detection

To prevent the player from splitting the bird after it has already hit the ground or the tower, a discrete collision callback (`on_collision_begin`) was registered directly into the physics `World`. 

The main state acts as an event router, listening to all impacts in the simulation. If a collision involves any of the active birds (ignoring invisible wind sensors), the router notifies the `BirdManager`. The manager then permanently disables the split ability for the remainder of that turn, ensuring the mechanic requires timing and skill to be used effectively mid-air.

## Turn resolution and camera cycling

Because the game now features multiple rigid bodies belonging to the player, the end-of-turn logic was overhauled. Instead of tracking a single entity, the `BirdManager` iterates through all active birds every frame. The turn only resets when every single bird drops below the linear and angular speed thresholds for a set amount of frames. 

To improve the player experience during the split, the camera was upgraded. While the birds are in flight and split, clicking anywhere on the screen cycles the camera's target focus between the primary bird, the upper clone, and the lower clone, updating the dynamic zoom and tracking smoothly.

## Controls

- Move Camera / Pan: Mouse Drag (starting anywhere else but the bird)
- Aim / Pull: Mouse Drag (starting near the bird)
- Split Bird: `Spacebar` (only while in flight, before impact)
- Cycle Camera Focus: `Left Click` (while in flight and split)
- Quit: `Escape`

## Project structure

- `main.py`: entry point of the game
- `settings.py`: constants, physics tuning, input bindings, graphics, and fonts
- `src/ThrowABird.py`: game bootstrap and main state machine
- `src/definitions/entity.py`: archetype definitions, mass, density formulas, and friction data
- `src/entity/BirdManager.py`: central manager for bird spawning, splitting, collision routing, and group idle checking
- `src/entity/Bird.py`: base dynamic circle body representing the projectile
- `src/entity/Destructible.py`: physical blocks tracking energy (HP) and applying damage based on impact speed
- `src/states/game/PlayState.py`: main interactive loop, input routing, collision dispatching, and camera logic
- `src/world/Level.py`: static ground, destructible block placement, and wind zones
- `assets/`: loose PNG graphics and fonts

## Running the project

```bash
cd 08-throw_a_bird
python main.py