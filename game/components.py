import pygame
import math
from enum import Enum, auto
from game import deebee as db

# --- CORE COMPONENT ---
class Component:
    """Base class for all components."""
    def update(self, owner, game, dt):
        pass
# --- GENERAL COMPONENTS ---
class VisualComponent(Component):
    """
    Manages the Pygame Surface (image) and Rect for the entity.
    Syncs the visual position with the physics position.
    """
    def __init__(self, color=(255, 255, 255), shape="circle", offset_x=0, offset_y=0):
        self.color = color
        self.shape = shape # "circle" or "rect"
        self.offset_x = offset_x
        self.offset_y = offset_y
        
        # Pygame Sprite Requirements
        # We create a transparent surface to draw on
        self.image = pygame.Surface((db.TILESIZE, db.TILESIZE), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        
        self._draw_internal()

    def _draw_internal(self):
        """Draws the shape onto the local image surface."""
        self.image.fill((0, 0, 0, 0)) # Clear with transparency
        
        if self.shape == "circle":
            radius = db.TILESIZE // 2
            pygame.draw.circle(self.image, self.color, (radius, radius), radius)
        elif self.shape == "rect":
            self.image.fill(self.color)

    def update(self, owner, game, dt):
        """
        Moves the Pygame Rect to match the Entity's world position.
        """
        # owner.pos_x / pos_y are the source of truth (from Physics or Init)
        self.rect.x = int(owner.pos_x + self.offset_x)
        self.rect.y = int(owner.pos_y + self.offset_y)


# --- STATS COMPONENTS ---

class StatsComponent(Component):
    """
    Tracks health and legacy equipment stats.
    """
    def __init__(self, hp=10, max_hp=10, equipment=None):
        self.hp = hp
        self.max_hp = max_hp
        self.equipment = equipment if equipment else {}
        # Backwards compatibility for the CombatSystem
        self.base_equipment_data = self.equipment 

# --- CONTROLLER COMPONENTS ---
class PlayerControlComponent(Component):
    """
    Translates InputManager actions into Physics velocity.
    """
    def update(self, owner, game, dt):
        # Check for InputManager (added in main.py)
        if not hasattr(game, 'input'): 
            return
            
        input_mgr = game.input
        dx, dy = 0, 0
        
        # Read Logical Actions (defined in engine/input.py)
        if input_mgr.is_pressed("UP"):    dy = -1
        if input_mgr.is_pressed("DOWN"):  dy = 1
        if input_mgr.is_pressed("LEFT"):  dx = -1
        if input_mgr.is_pressed("RIGHT"): dx = 1
        
        # Normalize vector (prevent fast diagonal movement)
        if dx != 0 or dy != 0:
            length = (dx*dx + dy*dy)**0.5
            dx /= length
            dy /= length
            
        # Get Speed from Physics or Default
        speed = 1.5 # Default walking speed (m/s)
        if hasattr(owner, 'physics') and hasattr(owner.physics, 'speed_mps'):
            speed = owner.physics.speed_mps
            
        # Apply to Physics
        if hasattr(owner, 'physics'):
            owner.physics.vx = dx * speed
            owner.physics.vy = dy * speed

class AIControlComponent(Component):
    """
    Basic Mob AI: Move towards target.
    """
    def __init__(self, target_name="player"):
        self.target_name = target_name
    
    def update(self, owner, game, dt):
        target = None
        
        # Resolve Target
        if self.target_name == "player":
            target = game.player
            
        # Simple Chase Logic
        if target and hasattr(target, 'physics') and hasattr(owner, 'physics'):
            tx, ty = target.physics.x, target.physics.y
            ox, oy = owner.physics.x, owner.physics.y
            
            dx = tx - ox
            dy = ty - oy
            dist = (dx*dx + dy*dy)**0.5
            
            # Stop if close enough (attack range)
            if dist > 0.5: 
                dx /= dist
                dy /= dist
                
                speed = 1.0 # Default mob speed
                if hasattr(owner.physics, 'speed_mps'):
                    speed = owner.physics.speed_mps
                    
                owner.physics.vx = dx * speed
                owner.physics.vy = dy * speed
            else:
                owner.physics.vx = 0
                owner.physics.vy = 0

# --- CORE ITEM LOGIC ---

class ItemComponent(Component):
    """
    Represents an object that can be stored in an inventory.
    Does NOT handle what the item *does* (eat, shoot, wear), only its logistics.
    """
    def __init__(self, name="Unknown", weight=0.1, volume=0.1, value=0, material=None):
        self.name = name
        self.base_weight = weight
        self.base_volume = volume
        self.value = value
        self.material = material
        self.condition = 100.0 # 0 to 100% durability
        self.is_equipped = False

    def update(self, owner, game, dt):
        pass

class StackableComponent(Component):
    """
    For Gold, Bullets, Seeds, Nails.
    Allows merging multiple entities into one logic object.
    """
    def __init__(self, count=1, max_stack=999):
        self.count = count
        self.max_stack = max_stack

class ContainerComponent(Component):
    """
    Allows an entity to hold other entities.
    Used for: Backpacks, Chests, Safes, Cars (trunk), Dressers.
    """
    def __init__(self, capacity_vol=10, capacity_weight=50, is_locked=False, key_id=None):
        self.capacity_vol = capacity_vol
        self.capacity_weight = capacity_weight
        self.content = [] # List of Entity objects
        
        # Locking Mechanics
        self.is_locked = is_locked
        self.key_id = key_id      # Matches a KeyComponent's id
        self.pick_difficulty = 50 # 1-100 skill check needed

    @property
    def total_weight(self):
        # Recursive weight: The container weighs its contents
        w = 0
        for entity in self.content:
            if hasattr(entity, 'item'):
                w += entity.item.base_weight
                # If the item inside is ALSO a container (nested), add its contents
                if hasattr(entity, 'container'):
                    w += entity.container.total_weight
            
            # Handle Stacks (Gold coins weight)
            if hasattr(entity, 'stack'):
                 w += (entity.item.base_weight * (entity.stack.count - 1))
        return w

    def add_item(self, item_entity):
        if self.is_locked:
            return False, "Locked"
        # Volume/Weight checks would go here
        self.content.append(item_entity)
        return True, "Added"

# --- FUNCTIONAL COMPONENTS (What items DO) ---

class EdibleComponent(Component):
    """
    For Apples, Cheese, Cooked Dishes.
    """
    def __init__(self, calories=100, hydration=0, spoil_rate=0.1, is_raw=False):
        self.calories = calories
        self.hydration = hydration
        self.spoil_rate = spoil_rate # How fast it rots per tick
        self.is_raw = is_raw # Requires cooking?

# components.py

class MaterialComponent(Component):
    def __init__(self, material_id: str, mass_kg: float):
        self.material_id = material_id # "oak", "steel", "flesh", "glass"
        self.mass = mass_kg
        
        # Current Physical State
        self.temperature = 20.0  # Celsius
        self.wetness = 0.0       # 0.0 to 1.0
        self.corrosion = 0.0     # 0.0 to 1.0 (Rust/Rot)
        self.integrity = 1.0     # 1.0 = Perfect, 0.0 = Destroyed
        self.is_burning = False
        
    def get_density(self):
        # Look up generic properties from the Material Database (see below)
        return self.weight / self.volume

class ToolComponent(Component):
    """
    For Hammers, Lockpicks, Needles, Anvils.
    """
    def __init__(self, tool_type, quality=1):
        self.tool_type = tool_type # "hammer", "lockpick", "needle"
        self.quality = quality     # Bonus to crafting rolls

class MeleeComponent(Component):
    def __init__(self, damage=10, reach=1.5, swing_speed=1.0, damage_type="slashing"):
        self.damage = damage
        self.reach = reach            # Distance in meters (tiles)
        self.swing_speed = swing_speed # Attacks per second
        self.damage_type = damage_type # slashing, piercing, blunt
        self.parry_window = 0.2       # Time window to block

class RangedComponent(Component):
    def __init__(self, damage=20, range_m=50, ammo_type="9mm", clip_size=12, noise_radius=20):
        self.damage = damage          # Base damage (bullet might override this)
        self.range = range_m
        self.ammo_type = ammo_type    # Tag to match with StackableComponent names
        self.clip_size = clip_size
        self.current_ammo = clip_size
        self.noise_radius = noise_radius # For stealth systems
        self.fire_mode = "semi"       # auto, semi, bolt
        self.recoil = 2.0

class WearableComponent(Component):
    """
    For Clothing, Armor, Accessories.
    Replaces/Augments the 'equip_tags' logic.
    """
    def __init__(self, layer: int, slots: list, warmth=0, stealth_penalty=0):
        self.layer = layer         # UNDERWEAR, OUTER, an int
        self.slots = slots         # ["head"], ["torso", "arms"], ["feet"]
        self.warmth = warmth       # For winter seasons
        self.stealth_penalty = stealth_penalty

# --- INTERACTION & ENVIRONMENT ---

class MechanismComponent(Component):
    """
    For Doors, Levers, Pressure Plates, Traps.
    """
    def __init__(self, is_active=False, trigger_type="manual"):
        self.is_active = is_active # Door Open / Trap Sprung
        self.trigger_type = trigger_type # "manual", "step", "remote"

    def toggle(self):
        self.is_active = not self.is_active

class VehicleComponent(Component):
    """
    For Cars, Boats, Carriages.
    """
    def __init__(self, max_speed=50, fuel_type="gas", fuel_capacity=100):
        self.max_speed = max_speed
        self.current_speed = 0
        self.fuel_type = fuel_type
        self.fuel_level = fuel_capacity
        self.is_engine_on = False

# --- UPDATED PHYSICS (Collision & Movement) ---

class PhysicsComponent(Component):
    """
    Updated to handle layer collision (flying, swimming, ground).
    """
    def __init__(self, x, y, is_static=False):
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.is_static = is_static # Furniture/Walls don't move
        
        # Movement Capabilities
        self.can_swim = False
        self.can_fly = False

    def update(self, owner, game, dt):
        if self.is_static: return
        
        # ... (Previous movement logic) ...
        # Add Terrain modifiers:
        # tile_type = game.map.get_tile(self.x, self.y)
        # if tile_type == "water" and not self.can_swim:
        #     self.sink_or_drown()

# --- BODY (Updated Equipping Logic) ---

class BodyComponent(Component):
    def __init__(self, body_plan_data):
        self.slots = {}     
        self.slot_tags = {} 
        
        # Initialize slots (same as before)
        for part in body_plan_data:
            name = part.get("name", "unknown")
            tags = part.get("tags", [])
            self.slots[name] = None
            self.slot_tags[name] = tags

    def equip(self, item_entity):
        """
        Updated to check WearableComponent layers and slots.
        """
        if not hasattr(item_entity, "wearable"):
             # Fallback to old system if no sophisticated component exists
             if hasattr(item_entity, "item"):
                 print("Item is not wearable.")
             return False
             
        wearable = item_entity.wearable
        
        # Check simple slot availability
        # In a real game, you'd check Layer overlap here 
        # (Can't wear Plate Armor over a Parka, etc.)
        
        for slot_req in wearable.slots:
            found_slot = False
            for body_slot, occupied in self.slots.items():
                if slot_req in self.slot_tags.get(body_slot, []):
                    if occupied is None:
                        self.slots[body_slot] = item_entity
                        found_slot = True
                        break
            if not found_slot:
                return False # Couldn't fit all required slots

        item_entity.item.is_equipped = True
        return True

class PickupComponent(Component):
    """
    Attached to an Entity to mark it as an item on the ground.
    Handles the transition from 'World Entity' back to 'Inventory Data'.
    """
    def __init__(self, pickup_radius=1.0, auto_pickup=False):
        self.pickup_radius = pickup_radius  # Distance in meters/tiles to interact
        self.auto_pickup = auto_pickup      # If True, simply walking over it grabs it (Mario style)
        
        # Visual/Animation state could go here later (e.g., hovering, rotating)
        self.hover_offset = 0.0