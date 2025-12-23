import json
import os
import logging
from game.deebee import DATA_DIR
from engine.base_entity import Entity
from game.components import *

logger = logging.getLogger(__name__)

# --- 1. ITEM SYSTEMS ---
def load_items():
    """
    Reads items.json and returns a dictionary of items keyed by ID.
    Returns: { "jeans": {...data...}, ... } or {} on error.
    """
    logger.debug("Loading items...")
    path = os.path.join(DATA_DIR, "items.json")
    if not os.path.exists(path):
        logger.warning(f"Items file not found at {path}")
        return {} 

    try:
        with open(path, 'r') as f:
            data = json.load(f)
            # Convert list to dict for faster lookups if data is a list
            count = len(data)
            if isinstance(data, list):
                logger.info(f"Loaded {count} items (from list).")
                return {item["id"]: item for item in data}
            logger.info(f"Loaded {count} items (from dict).")
            return data
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding items.json: {e}")
        return {}

def create_item(game, item_id, definitions):
    """
    Factory to create an item entity from a definition ID.
    """
    if definitions is None:
        logger.error("Item definitions are None")
        return None
        
    if item_id not in definitions:
        logger.warning(f"Item ID '{item_id}' not defined.")
        return None
    
    data = definitions[item_id]
    
    # Create Entity (let game decide where to put it)
    e = Entity(game)
    
    # 1. Item Metadata
    e.item = ItemComponent(
        name=data.get("name", "Unknown"),
        weight=data.get("weight", 0.1),
        volume=data.get("volume", 0.1),
        value=data.get("value", 0),
        material=data.get("material", None)
    )
    
    # 2. Wearable Logic
    slots = data.get("slots", [])
    layer = data.get("layer", None)
    
    if slots or layer is not None:
        # Default layer to 1 (Outer) if unspecified but slots exist
        if layer is None: layer = 1 
        e.wearable = WearableComponent(layer=layer, slots=slots)

    # 3. Container Logic
    tags = data.get("tags", [])
    if "container" in tags or "container_capacity" in data:
        cap_vol = data.get("container_capacity", 10)
        e.container = ContainerComponent(capacity_vol=cap_vol)
        
    return e

# --- 2. LOADOUT SYSTEMS ---
def load_loadouts():
    """Reads loadouts.json."""
    logger.debug("Loading loadouts...")
    path = os.path.join(DATA_DIR, "loadouts.json")
    if not os.path.exists(path):
        return {}
    try:
        with open(path, 'r') as f:
            data = json.load(f)
            logger.info(f"Loaded {len(data)} loadouts.")
            return data
    except Exception as e:
        logger.error(f"Error loading loadouts: {e}")
        return {}

def validate_loadouts(loadouts, item_defs):
    """
    Ensures every item in the loadouts actually exists in item_defs.
    """
    if not loadouts or not item_defs:
        return {}
        
    sanitized = {}
    for lo_name, gear_list in loadouts.items():
        valid_gear = []
        for item_id in gear_list:
            if item_id in item_defs:
                valid_gear.append(item_id)
            else:
                logger.warning(f"Loadout '{lo_name}' contains unknown item '{item_id}'. Removed.")
        sanitized[lo_name] = valid_gear
        
    return sanitized

# --- 3. ANATOMY SYSTEMS ---
def flatten_body_plan(node, parent_tags=None):
    if parent_tags is None: parent_tags = []
    
    inheritable = {"left", "right", "front", "back"}
    inherited = [t for t in parent_tags if t in inheritable]
    
    current_tags = node.get("tags", []) + inherited
    
    base_name = node["name"]
    unique_name = base_name
    if "left" in current_tags and "left" not in base_name: unique_name += "_left"
    elif "right" in current_tags and "right" not in base_name: unique_name += "_right"
    
    flat_list = [{
        "name": unique_name,
        "tags": list(set(current_tags)), 
        "base_name": base_name
    }]
    
    for child in node.get("inside", []):
        flat_list.extend(flatten_body_plan(child, current_tags))
    for child in node.get("subparts", []):
        flat_list.extend(flatten_body_plan(child, current_tags))
            
    return flat_list

def load_body_plans():
    logger.debug("Loading body plans...")
    path = os.path.join(DATA_DIR, "body_plan_fantasy.json")
    if not os.path.exists(path):
        logger.warning("Body Plan file missing")
        return {}
    
    try:
        with open(path, 'r') as f:
            raw = json.load(f)
        
        parsed = {}
        for entry in raw:
            for race, root_list in entry.items():
                flattened = []
                for root_node in root_list:
                    flattened.extend(flatten_body_plan(root_node))
                parsed[race] = flattened
        logger.info(f"Loaded body plans for: {list(parsed.keys())}")
        return parsed
        
    except Exception as e:
        logger.error(f"Body Plan Error: {e}")
        return {}

# --- 4. MATERIAL SYSTEMS ---
def load_materials():
    """
    Loads material definitions from materials.json.
    Returns: { "steel": {...}, "oak": {...} } or {} on error.
    """
    logger.debug("Loading materials...")
    path = os.path.join(DATA_DIR, "materials.json")
    
    if not os.path.exists(path):
        logger.warning(f"Material file not found at {path}")
        return {}

    try:
        with open(path, 'r') as f:
            raw_data = json.load(f)
            
        materials = {}
        # Get defaults to prevent key errors later
        default_mat = raw_data.get("default", {})
        
        for key, props in raw_data.items():
            # Merge props onto the default template
            final_props = default_mat.copy()
            final_props.update(props)
            materials[key] = final_props
            
        logger.info(f"Loaded {len(materials)} materials.")
        return materials
        
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding materials.json: {e}")
        return {}

def load_mobs():
    """
    Reads mobs.json and returns a dictionary of mob definitions.
    """
    logger.debug("Loading mobs...")
    path = os.path.join(DATA_DIR, "mobs.json")
    if not os.path.exists(path):
        logger.warning(f"Mobs file not found at {path}")
        return {} 

    try:
        with open(path, 'r') as f:
            data = json.load(f)
            logger.info(f"Loaded {len(data)} mob definitions.")
            return data
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding mobs.json: {e}")
        return {}

# --- 5. CONFIGURATION SYSTEMS ---
# in deebee.py