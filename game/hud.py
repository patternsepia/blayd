import pygame
import logging
from game.deebee import *
from engine import colors as cn

logger = logging.getLogger(__name__)

class HUD:
    def __init__(self):
        self.font = pygame.font.SysFont("arial", 20)
        self.bar_length = 200
        self.bar_height = 10
        logger.info("HUD initialized.")

    def draw(self, surface, player):
        # 1. Safety Check (Player might be dead/None)
        if not player:
            return

        # 2. Stats
        hp = player.stats.hp
        max_hp = player.stats.max_hp
        
        # --- FIX: Weapon Resolution ---
        weapon_name = "Unarmed"
        
        # A. Try to find what is actually held in hands (Body System)
        if hasattr(player, "body") and player.body:
            for slot_name, item_entity in player.body.slots.items():
                if item_entity:
                    # Check if the slot is meant for grasping (hands)
                    # We check the tags associated with this specific body part
                    slot_tags = player.body.slot_tags.get(slot_name, [])
                    if "grasp" in slot_tags:
                        # Found an item in a hand, use its name
                        if hasattr(item_entity, "item"):
                            weapon_name = item_entity.item.name
                            break

        # B. Fallback to stats default (Legacy System) if still unarmed
        if weapon_name == "Unarmed" and hasattr(player.stats, "base_equipment_data"):
            # Use .get() to avoid crashes if keys are missing
            weapon_data = player.stats.base_equipment_data.get('weapon', {})
            weapon_name = weapon_data.get('name', "Unarmed")

        # 3. Draw Health Bar
        # Background (Red)
        outline_rect = pygame.Rect(10, 10, self.bar_length, self.bar_height)
        pygame.draw.rect(surface, (60, 60, 60), outline_rect) 
        
        # Foreground (Green/Health)
        if max_hp > 0:
            pct = max(0, hp / max_hp)
        else:
            pct = 0
            
        fill_rect = pygame.Rect(10, 10, int(self.bar_length * pct), self.bar_height)
        col = cn.get("green") if pct > 0.5 else (255, 255, 0) if pct > 0.2 else cn.get("red")
        pygame.draw.rect(surface, col, fill_rect)
        pygame.draw.rect(surface, cn.get("white"), outline_rect, 2) # Border

        # 4. Draw Text
        self.draw_text(surface, f"{hp:.0f}/{max_hp:.0f}", 220, 10)
        self.draw_text(surface, f"Wpn: {weapon_name}", 10, 40)
        self.draw_text(surface, "WASD to Move | S to Save | ESC for Menu | I for Inventory", 10, HEIGHT - 30)

        # Draw Seed (Bottom Right)
        if hasattr(player.game.map, 'seed'):
            seed_text = f"Seed: {player.game.map.seed}"
            text_surf = self.font.render(seed_text, True, cn.get("springgreen"))
            rect = text_surf.get_rect(bottomright=(WIDTH - 10, HEIGHT - 10))
            surface.blit(text_surf, rect)

    def draw_text(self, surface, text, x, y):
        text_surface = self.font.render(text, True, cn.get("white"))
        surface.blit(text_surface, (x, y))