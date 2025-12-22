import json
import os
import pygame
from game.deebee import SAVE_FILE, TILESIZE, GRID_WIDTH, GRID_HEIGHT
from game.map_gen import Map
from game.entities import create_player, create_mob

from game.systems import CombatSystem

def save_game_state(game):
    """
    Serializes the current game state to a JSON file.
    Returns True if successful, False if failed.
    """
    if not game.player or not game.map:
        print("Error: Cannot save, game state is invalid.")
        return False

    # 1. Gather Data
    data = {
        "seed": game.map.seed,
        "player": {
            # Save Grid Coords (Float -> Int/Grid)
            "x": game.player.physics.x / TILESIZE, 
            "y": game.player.physics.y / TILESIZE,
            "hp": game.player.stats.hp,
            "equipment": game.player.stats.equipment
            # TODO: Future - Serialize BodyComponent/Inventory Hierarchy here
        },
        "map_grid": game.map.grid, 
        "mobs": [
            {
                "x": m.physics.x / TILESIZE, 
                "y": m.physics.y / TILESIZE, 
                "hp": m.stats.hp
            } for m in game.mobs
        ]
    }
    
    # 2. Write File
    try:
        with open(SAVE_FILE, 'w') as f:
            json.dump(data, f)
        print(f"Game Saved to {SAVE_FILE}")
        return True
    except Exception as e:
        print(f"Error saving game: {e}")
        return False

def load_game_state(game):
    """
    Reads the JSON file and reconstructs the Game object's state in-place.
    Returns True if successful, False if failed.
    """
    if not os.path.exists(SAVE_FILE):
        print("No save file found.")
        return False
    
    try:
        with open(SAVE_FILE, 'r') as f:
            data = json.load(f)

        # 1. Restore Map
        # We prefer the seed to regenerate the exact same map, 
        # but we overwrite with the saved grid in case the map was modified (digging/destruction)
        seed = data.get("seed", None)
        game.map = Map(GRID_WIDTH, GRID_HEIGHT, seed=seed)
        if "map_grid" in data:
            game.map.grid = data["map_grid"]
        
        # 2. Reset Sprite Groups
        game.all_sprites = pygame.sprite.Group()
        game.mobs = pygame.sprite.Group()

        # 3. Restore Player
        p_data = data["player"]
        # We explicitly pass X and Y to prevent the factory from auto-spawning
        game.player = create_player(game, game.item_defs, x=p_data["x"], y=p_data["y"])
        
        # Restore Stats
        game.player.stats.hp = p_data["hp"]
        game.player.stats.equipment = p_data["equipment"]
        
        game.all_sprites.add(game.player)

        # 4. Restore Mobs
        for m_data in data["mobs"]:
            m = create_mob(game, x=m_data["x"], y=m_data["y"])
            m.stats.hp = m_data["hp"]
            game.all_sprites.add(m)
            game.mobs.add(m)

        # 5. Re-Initialize Systems
        # The Inventory UI must be relinked to the new Player entity
        game.combat_system = CombatSystem()

        print("Game Loaded Successfully!")
        return True
        
    except Exception as e:
        print(f"Error loading save: {e}")
        # Consider printing full traceback here for debugging
        import traceback
        traceback.print_exc()
        return False