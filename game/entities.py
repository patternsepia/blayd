from engine.base_entity import Entity
from engine.colors import *
from game.components import (
    VisualComponent, 
    PhysicsComponent, 
    PlayerControlComponent, 
    StatsComponent, 
    BodyComponent,
    AIControlComponent,
    PickupComponent
)
from game.deebee import *
from game.loader import create_item

def create_player(game, x=None, y=None, loadout_key="default"):
    """
    Creates the Player Entity.
    """
    # 1. SPAWN LOGIC (Safety First)
    if x is None or y is None:
        x, y = game.map.find_open_space(radius=1, bias="top_left")
        print(f"DEBUG: Spawning player at {x}, {y}")
    
    # 2. CORE COMPONENTS
    e = Entity(game, x, y)
    e.visual = VisualComponent()
    e.physics = PhysicsComponent(x, y, speed_mps=1.5)
    e.control = PlayerControlComponent()
    e.stats = StatsComponent(hp=100, max_hp=100, equipment={
        "weapon": {"name": "Fists", "atk": 1},
        "armor": {"name": "Skin", "def": 0}
    })
    
    # 3. ANATOMY SETUP
    humanoid_data = game.body_plans.get("humanoid", [{"name": "chest", "tags": ["torso", "wear"]}])
    e.body = BodyComponent(humanoid_data)
    
    # 3. LOADOUT
    gear_list = game.loadouts.get(loadout_key, [])
    
    if not gear_list:
        print(f"Warning: Loadout '{loadout_key}' is empty or missing.")

    created_items = []
    
    # A. Instantiate Items
    for item_id in gear_list:
        item = create_item(game, item_id, game.item_defs)
        if item:
            created_items.append(item)
        else:
            print(f"Warning: Item '{item_id}' in loadout '{loadout_key}' not found.")

    # B. Equip Phase
    leftovers = []
    for item in created_items:
        if not e.body.equip(item):
            leftovers.append(item)

    # C. Stash Phase
    if leftovers:
        best_container = None
        max_capacity = -1

        for slot_name, equipped_item in e.body.slots.items():
            if equipped_item and hasattr(equipped_item, 'container') and equipped_item.container:
                if equipped_item.container.capacity > max_capacity:
                    max_capacity = equipped_item.container.capacity
                    best_container = equipped_item

        if best_container:
            for item in leftovers:
                best_container.container.items.append(item)
        else:
            print(f"Dropped {len(leftovers)} items (No container space)")

    e.refresh_visuals()
    return e

def create_mob(game, x=None, y=None):
    """
    Creates a basic enemy (Goblin).
    """
    # 1. SPAWN LOGIC
    if x is None or y is None:
        x, y = game.map.find_open_space(radius=1, bias="bottom_right")
    
    e = Entity(game, x, y)
    
    # 2. VISUALS & PHYSICS
    e.visual = VisualComponent(pygame.Color(128, 64, 0)) 
    e.physics = PhysicsComponent(x, y, speed_mps=1.0)
    
    # --- FIX: GIVE MOB A BRAIN ---
    e.control = AIControlComponent(target_name="player") 
    
    # 3. STATS
    e.stats = StatsComponent(hp=30, max_hp=30, equipment={
        "weapon": {"name": "Claws", "atk": 2},
        "armor": {"name": "Rags", "def": 0}
    })

    # 4. ANATOMY SETUP
    mob_data = game.body_plans.get("goblin", game.body_plans.get("humanoid", []))
    e.body = BodyComponent(mob_data)
    
    # 5. MOB LOADOUT
    mob_gear = ["combat_knife"] 
    
    for item_id in mob_gear:
        item = create_item(game, item_id, game.item_defs)
        
        if item:
            if not e.body.equip(item):
                print(f"Mob at {x},{y} failed to equip {item_id}")
                item.kill() 
            else:
                print(f"Mob equipped {item_id}")

    e.refresh_visuals()
    return e
def create_world_item(game, item_id, x, y):
    """
    Spawns an item on the ground at specific coordinates.
    """
    # 1. Create the Base Entity
    e = Entity(game, x, y)
    
    # 2. Physics (Items are usually static unless you have gravity/throwing)
    # We set is_static=True so they don't slide around, or False if you want them to be pushed.
    e.physics = PhysicsComponent(x, y, is_static=True)
    
    # 3. The Item Data (The "Soul" of the item)
    # We use your existing loader to fetch the raw data stats
    item_component = create_item(game, item_id, game.item_defs)
    
    if not item_component:
        print(f"ERROR: Could not spawn {item_id} - definition not found.")
        e.kill()
        return None

    # Attach the data to this world entity
    # Note: Depending on your engine, you might attach the components *of* the item 
    # to this entity, or store the item object inside a wrapper. 
    # Assuming direct attachment based on your architecture:
    e.item = item_component.item  # The ItemComponent
    if hasattr(item_component, 'stack'): e.stack = item_component.stack
    if hasattr(item_component, 'wearable'): e.wearable = item_component.wearable
    if hasattr(item_component, 'tool'): e.tool = item_component.tool
    # ... transfer other components as needed ...

    # 4. The Pickup Logic
    e.pickup = PickupComponent()

    # 5. Visuals (Placeholder)
    # We use a distinct color (e.g., Gold/Yellow) to differentiate from Mobs (Red)
    e.visual = VisualComponent(color=pygame.Color("gold"))
    
    # Optional: Scale it down so it looks smaller than a person
    # if hasattr(e.visual, 'rect'):
    #     e.visual.rect.inflate_ip(-10, -10) 

    return e