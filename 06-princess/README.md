# The Legend of the Princess with Bow, Boss Arena and Fireball Combat

This project is a dungeon-crawler action RPG built with Python, Pygame and Gale. The base gameplay follows a classic top-down exploration loop: the player walks through rooms, fights enemies, interacts with objects, opens doors, and survives encounters while moving through a dungeon.

## Original game

The original concept is a Zelda-like ARPG in which the player explores a series of interconnected rooms, defeats hostile creatures and eventually faces a boss. The core mechanics are based on four-direction movement, sword attacks, room transitions and basic survival combat. Items and environmental props add depth, but the gameplay remains centered on exploration and combat.

This project preserves that room-based dungeon structure but extends it with a more defined progression loop and boss encounter.

## Change implemented

The main delivered enhancement is the addition of a ranged combat path built around a chest reward and a boss arena challenge:

1. A random chest that grants a bow.
2. Arrow firing using the Bow + Projectile factory pattern.
3. Boss-room generation after obtaining the bow.
4. A boss with hitpoints, immunity and vulnerability windows.
5. Fireball-based ranged attacks that punish mistakes.
6. A clearer dungeon objective, driven by the boss encounter instead of generic room crawling alone.

## Chest and bow system

The dungeon generates a chest in a room with a low random chance, and only one chest can be spawned at a time before the player receives the bow. The player must stand adjacent to it and interact with it to open it.

When opened, the chest changes state and drops a bow item. Once the player collects it, the combat options expand: the character can now shoot arrows in the direction it is facing. The bow logic is implemented in `Bow.fire()`, which creates a projectile from the player's position and delegates the motion to the `Projectile` class.

## Boss room and room progression

Once the player has the bow, room generation begins favoring boss-room access after a few normal rooms. The boss area is intentionally more constrained than a standard dungeon room: there are no enemies, no pots, no extra switches, and only the boss on the opposite side of the entrance door.

## Boss behavior

The boss has a health value and follows a simple combat cycle:

- it chases the player for a short period
- it pauses and attacks by firing slow fireballs toward the player's current position
- it remains active until defeated

The fireball attack is a slow projectile that is aimed at the player's location at the moment it is created. If the player is hit, the game ends immediately. This makes movement, spacing and reaction time essential during the boss fight.

## Boss vulnerability and melee interaction

The boss is immune to sword attacks, but vulnerable to arrows. Every time an arrow hits the boss, the immunity window is temporarily removed, which creates a brief opening in which the player can damage it with the sword.

This creates a rhythm in combat:
- use the bow to break the boss's defense
- attack during the exposed window
- avoid the fireball barrage and direct body contact

If the player touches the boss directly, the boss deals a full heart of damage.

## Player damage and survival rules

The project keeps the original dungeon formula while reinforcing danger with a more explicit combat pressure system:

- direct boss contact causes a full heart loss
- fireballs instantly kill the player on impact
- regular enemy contact deals standard damage
- heart pickups can be used to recover health when available

## Controls

- Move: Arrow keys
- Sword attack: Space
- Interact: Enter
- Shoot bow: Z
- Dance / alternate animation: C
- Quit: Escape

## Project structure

- `main.py`: entry point of the game
- `settings.py`: constants, input bindings, textures, sounds and music
- `src/TheLegendOfThePrincess.py`: game bootstrap and state machine
- `src/Player.py`: player entity, movement and arcadey interaction logic
- `src/Bow.py`: bow logic and arrow creation using the Factory pattern
- `src/Projectile.py`: projectile movement and render logic
- `src/Fireball.py`: boss projectile logic and fireball animation
- `src/world/Dungeon.py`: room generation, chest logic and boss-room flow
- `src/world/Room.py`: room creation, enemies, objects and boss room behavior
- `src/world/Doorway.py`: room transitions and door logic
- `src/states/entity/`: player and boss AI/state logic
- `assets/`: sprites, music and sound effects used by the game

## Running the project

```bash
cd 06-princess
python main.py
```
