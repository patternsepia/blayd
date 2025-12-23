# Blayd Copilot Instructions

## Architecture Overview
Blayd is a Pygame-based medieval roguelike using Entity-Component-System (ECS) architecture. Core separation:
- **Entities** (`engine/base_entity.py`): Game objects with attached components
- **Components** (`game/components.py`): Data/logic units (Visual, Physics, Stats, Control)
- **Systems** (`game/systems.py`): Update logic operating on entities with specific components

## Key Patterns
- **Component Attachment**: Entities get components via `entity.visual = VisualComponent(...)`
- **System Updates**: Systems like `CombatSystem.update(player, mobs)` handle interactions
- **Data-Driven Design**: Game data from JSON files in `data/` loaded via `game/loader.py`
- **State Management**: `engine/events.py` StateManager handles menu/roaming states
- **Constants**: All game constants in `game/deebee.py` (e.g., TILESIZE=16)

## Development Workflow
- Run game: `python main.py`
- Add entities: Use factory functions in `game/entities.py`
- Modify data: Edit JSON in `data/`, reload via loader functions
- Save/load: `game/persist.py` serializes to `data/saves/savegame.json`

## Code Style
- Components inherit from `Component` base class
- Use `hasattr(entity, 'component')` for safe component checks
- Position in tiles: `pos_x/y` in pixels, grid coords divide by TILESIZE
- Update order: Control → Physics → Visual in entity.update()

## Examples
- Create mob: `mob = create_mob(game, "goblin", x=5, y=5)`
- Add physics: `entity.physics = PhysicsComponent(x=10*TILESIZE, y=10*TILESIZE)`
- Handle input: Check `game.input.is_pressed("UP")` in control components