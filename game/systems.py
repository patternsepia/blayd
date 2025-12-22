import pygame
import random
from game.deebee import *

class CombatSystem:
    def update(self, player, mobs):
        """
        Handles combat interactions between the player and mobs.
        """
        # 1. Player hits Mobs (Attack)
        # using spritecollide(sprite, group, dokill, collided)
        hits = pygame.sprite.spritecollide(player, mobs, False)
        for mob in hits:
            # Simulation: Calculate Damage
            weapon_dmg = 1 # Default (Fists/Unarmed)
            
            # A. Check New Body System (Prioritize what is effectively held)
            weapon_found = False
            if hasattr(player, "body") and player.body:
                for slot_name, item_entity in player.body.slots.items():
                    if item_entity:
                        # Check if this slot is a hand (grasping slot)
                        slot_tags = player.body.slot_tags.get(slot_name, [])
                        if "grasp" in slot_tags:
                            # Found an item in hand. 
                            # Since items.json currently lacks 'atk' stats, we assign generic damage
                            # based on the fact that they are holding *something*.
                            # (Future: check item_entity.item.tags for 'weapon')
                            weapon_dmg = 4 
                            weapon_found = True
                            break
            
            # B. Fallback to Legacy Stats System (if no weapon held)
            if not weapon_found and hasattr(player, "stats"):
                # Safe access to the dictionary to prevent crashes
                legacy_gear = getattr(player.stats, "base_equipment_data", {})
                weapon_data = legacy_gear.get("weapon", {})
                weapon_dmg = weapon_data.get("atk", 1)

            # Apply Damage
            if hasattr(mob, "stats"):
                mob.stats.hp -= weapon_dmg
                print(f"Hit Mob! Damage: {weapon_dmg} | Mob HP: {mob.stats.hp}")
            
            # Simulation: Knockback
            # Simple physics bounce: if player moving right, push mob right
            # (Check if physics component exists to prevent crash)
            if hasattr(player, "physics") and hasattr(mob, "physics"):
                push_x = 5 if player.physics.vx > 0 else -5
                push_y = 5 if player.physics.vy > 0 else -5
                
                mob.physics.vx += push_x
                mob.physics.vy += push_y

            if hasattr(mob, "stats") and mob.stats.hp <= 0:
                mob.kill()

        # 2. Mobs hit Player (Optional: Add this logic here later)

class MaterialSystem:
    def __init__(self, material_db):
        self.material_db = material_db

    def update(self, game_context, dt):
        # 1. Get Global Context from the passed 'game_context'
        # Ensure game_context has a 'weather' attribute (e.g. game.weather)
        # If 'weather' isn't implemented yet, handle that safety check.
        weather = getattr(game_context, "weather", None)
        current_weather = weather.current if weather else "none"
        temp = weather.temperature if weather else 20
        
        # 2. Iterate Entities
        # We access entities from the game_context
        for sprite in game_context.all_sprites:
            if hasattr(sprite, 'material'):
                mat = sprite.material
                
                # Use the injected DB, not a global
                props = self.material_db.get(mat.material_id, {})
                
                # --- PHASE A: IMMEDIATE PHYSICS ---
                if current_weather == "rain": # and check shelter...
                     mat.wetness = min(1.0, mat.wetness + dt * 0.1)
                else:
                     mat.wetness = max(0.0, mat.wetness - dt * 0.05)
                
                # --- PHASE B: REACTIONS ---
                if props.get("rusts", False) and mat.wetness > 0.5:
                    damage = 0.001 * dt 
                    mat.integrity -= damage

                if props.get("rots", False):
                    rate = 0.001
                    if temp > 30: rate *= 2
                    if mat.wetness > 0.5: rate *= 2
                    mat.integrity -= rate * dt

def attempt_stash_item(player, item_entity):
    """
    Tries to add item to: 1. Largest worn container, 2. Hands.
    Returns (True, "Reason") or (False, "Reason").
    """
    # 1. Containers
    containers = []
    if player.body:
        for slot, equipped in player.body.slots.items():
            if equipped and hasattr(equipped, 'container'):
                containers.append(equipped.container)
    
    # Sort largest capacity first
    containers.sort(key=lambda c: c.capacity_vol, reverse=True)
    
    for c in containers:
        success, msg = c.add_item(item_entity)
        if success: return True, f"Stored in {c.owner.item.name}"

    # 2. Hands
    if player.body:
        for slot, tags in player.body.slot_tags.items():
            if "grasp" in tags and player.body.slots[slot] is None:
                player.body.slots[slot] = item_entity
                item_entity.item.is_equipped = True
                return True, "Held in hand"

    return False, "Inventory full"