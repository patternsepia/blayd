import pygame
import sys
import random

from engine.events import GameState
from engine import colors as cn
# IMPORT THE NEW UI ELEMENTS
from engine.ui import Label, Button, VBox, InputBox 

from game.deebee import *
from game.components import PhysicsComponent, PickupComponent
from game.systems import attempt_stash_item

class GameState:
    def handle_input(self, input_mgr): pass # For Actions (Movement, UI Nav)
    def handle_event(self, event): pass     # For Raw Events (Typing)

# --- 1. MAIN MENU STATE ---
class MainMenuState(GameState):
    def __init__(self, game):
        super().__init__(game)
        self.font = pygame.font.SysFont("arial", 24)
        
        # 1. Title Label
        self.title = Label(50, 50, TITLE, pygame.font.SysFont("arial", 60, bold=True))
        
        # 2. Menu Container (VBox)
        # Center X, Center Y roughly
        cx = WIDTH // 2 - 100
        cy = HEIGHT // 2
        self.menu_box = VBox(cx, cy, 200, padding=10)
        
        # 3. Add Buttons
        self.menu_box.add_child(Button(0,0,0,40, "New Game [N]", self.font, self.game.new_game, pygame.K_n))
        self.menu_box.add_child(Button(0,0,0,40, "Load Game [L]", self.font, self.game.load_game, pygame.K_l))
        self.menu_box.add_child(Button(0,0,0,40, "Seed Game [S]", self.font, 
                                       lambda: self.game.state_machine.push(SeedInputState(self.game)), pygame.K_s))
        self.menu_box.add_child(Button(0,0,0,40, "Quit [Q]", self.font, sys.exit, pygame.K_q))
        
        # Select first item by default
        self.menu_box.selection_index = 0
        self.menu_box._update_selection()

    def handle_input(self, input_mgr):
        # Delegate to UI
        self.menu_box.handle_event(input_mgr)

    def draw(self, screen):
        bg = self.game.c.get('colors', {}).get('ui', {}).get('bg_color', cn.BLACK)
        screen.fill(bg)
        
        self.title.draw(screen)
        if self.game.custom_seed:
            lbl = self.font.render(f"Seed: {self.game.custom_seed}", True, cn.GREEN)
            screen.blit(lbl, (50, 120))
            
        self.menu_box.draw(screen)


# --- 2. PAUSE STATE ---
class PauseState(GameState):
    def __init__(self, game):
        super().__init__(game)
        self.font = pygame.font.SysFont("arial", 24)
        
        cx = WIDTH // 2 - 100
        cy = HEIGHT // 2 - 100
        
        # Container
        self.menu_box = VBox(cx, cy, 200, padding=10)
        self.menu_box.add_child(Button(0,0,0,40, "Resume [Esc]", self.font, lambda: self.game.state_machine.pop(), pygame.K_ESCAPE))
        self.menu_box.add_child(Button(0,0,0,40, "Save [S]", self.font, self.game.save_game, pygame.K_s))
        self.menu_box.add_child(Button(0,0,0,40, "Load [L]", self.font, self.game.load_game, pygame.K_l))
        self.menu_box.add_child(Button(0,0,0,40, "Main Menu [M]", self.font, 
                                       lambda: self.game.state_machine.set(MainMenuState(self.game)), pygame.K_m))
        self.menu_box.add_child(Button(0,0,0,40, "Quit [Q]", self.font, sys.exit, pygame.K_q))

        self.menu_box.selection_index = 0
        self.menu_box._update_selection()

    def handle_input(self, event):
        self.menu_box.handle_event(event)

    def draw(self, screen):
        # Overlay logic
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))
        
        # Draw a backing panel for the menu
        panel_rect = pygame.Rect(self.menu_box.rect.x - 20, self.menu_box.rect.y - 20, 
                                 self.menu_box.rect.width + 40, self.menu_box.rect.height + 40)
        pygame.draw.rect(screen, (40, 40, 50), panel_rect)
        pygame.draw.rect(screen, cn.WHITE, panel_rect, 2)
        
        self.menu_box.draw(screen)


# --- 3. SEED INPUT STATE ---
class SeedInputState(GameState):
    def __init__(self, game):
        super().__init__(game)
        self.font = pygame.font.SysFont("arial", 24)
        
        cx = WIDTH // 2 - 150
        cy = HEIGHT // 2
        
        self.label = Label(cx, cy - 40, "Enter Map Seed:", self.font)
        self.input_box = InputBox(cx, cy, 300, 40, self.font)
        
    def handle_input(self, event):
        # 1. Global Keys
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                if self.input_box.text.strip():
                    self.game.custom_seed = self.input_box.text
                self.game.state_machine.pop()
                return
            elif event.key == pygame.K_ESCAPE:
                self.game.state_machine.pop()
                return
        
        # 2. Widget Specific
        self.input_box.handle_event(event)

    def draw(self, screen):
        # Darken background
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))
        
        self.label.draw(screen)
        self.input_box.draw(screen)


# --- 4. ROAMING & GAMEPLAY (Unchanged UI logic for now) ---
# Note: InventoryState is complex data-binding. 
# For now, it is okay to keep the specialized render logic in InventoryState 
# until we build a "DataGrid" or "ListView" widget in engine/ui.py.

class RoamingState(GameState):
    def handle_input(self, input_mgr):
        # 1. Global Toggles
        if input_mgr.is_just_pressed("CANCEL"): # ESC
            self.game.state_machine.push(PauseState(self.game))
        elif input_mgr.is_just_pressed("INVENTORY"):
            self.game.state_machine.push(InventoryState(self.game))
        
        # 2. Player Movement
        # We can pass the input manager directly to the player control component
        if self.game.player and hasattr(self.game.player, 'control'):
            self.game.player.control.update(self.game.player, self.game, input_mgr)
    def update(self):
        if self.game.all_sprites:
            self.game.all_sprites.update(self.game.dt)
        if self.game.combat_system:
            self.game.combat_system.update(self.game.player, self.game.mobs)

    def draw(self, screen):
        screen.fill(self.game.c.get('BG_COLOR', cn.BLACK))
        self.game.draw_grid()
        if self.game.all_sprites:
            self.game.all_sprites.draw(screen)
        if self.game.player:
            self.game.hud.draw(screen, self.game.player)


# --- 5. LEGACY STATES (Inventory / Pickup) ---
# These are preserved as-is from the previous step because they require 
# highly specific rendering (item lists, status bars) that generic buttons 
# don't handle well yet without a more advanced "ListView" widget.

class InventoryState(GameState):
    # ... (Keep the exact code from the previous response for InventoryState) ...
    def __init__(self, game):
        super().__init__(game)
        self.font_main = pygame.font.SysFont("arial", 16)
        self.font_header = pygame.font.SysFont("arial", 18, bold=True)
        self.font_status = pygame.font.SysFont("consolas", 14)
        
        self.current_container = None 
        self.selection_index = 0
        self.visible_items = []

    def enter(self):
        self.rebuild_list()
        self.selection_index = 0
        self.current_container = None

    def rebuild_list(self):
        # ... (Same logic as before) ...
        player = self.game.player
        if self.current_container:
            if hasattr(self.current_container, 'container') and self.current_container.container:
                 self.visible_items = list(reversed(self.current_container.container.items))
            else:
                 self.visible_items = []
            if self.visible_items: self.selection_index %= len(self.visible_items)
            else: self.selection_index = 0
            return

        self.visible_items = []
        worn, carried, nearby = [], [], []
        body = player.body
        seen = set()

        for slot in body.slot_order:
            item = body.slots.get(slot)
            if item and item not in seen:
                seen.add(item)
                tags = body.slot_defs.get(slot, [])
                if "grasp" in tags or "hold" in tags: carried.append((item, slot))
                else: worn.append((item, slot))

        px, py = (int(player.physics.x), int(player.physics.y)) if player.physics else (0,0)
        for sprite in self.game.all_sprites:
            if sprite != player and hasattr(sprite, 'item') and sprite.item and hasattr(sprite, 'physics') and sprite.physics:
                if not sprite.item.is_equipped:
                    if abs(int(sprite.physics.x) - px) <= 1 and abs(int(sprite.physics.y) - py) <= 1:
                        nearby.append(sprite)
        
        carried.sort(key=lambda x: x[0].item.name)
        if worn: self.visible_items.append("WORN"); self.visible_items.extend(worn)
        if carried: self.visible_items.append("CARRIED"); self.visible_items.extend(carried)
        if nearby: self.visible_items.append("NEARBY"); self.visible_items.extend([(x, "Ground") for x in nearby])

        if not self.visible_items: self.selection_index = 0
        elif self.selection_index >= len(self.visible_items): self.selection_index = len(self.visible_items) - 1

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_i:
                self.game.state_machine.pop()
            elif event.key == pygame.K_UP: self._move(-1)
            elif event.key == pygame.K_DOWN: self._move(1)
            elif event.key == pygame.K_RIGHT or event.key == pygame.K_PERIOD: self._enter_c()
            elif event.key == pygame.K_LEFT or event.key == pygame.K_COMMA: self._exit_c()
            elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS: self._exec("+")
            elif event.key == pygame.K_MINUS: self._exec("-")
            elif event.key == pygame.K_d: self._exec("d")

    def _move(self, delta):
        if not self.visible_items: return
        count = len(self.visible_items)
        new_idx = (self.selection_index + delta) % count
        attempts = 0
        while isinstance(self.visible_items[new_idx], str) and attempts < count:
            new_idx = (new_idx + delta) % count
            attempts += 1
        self.selection_index = new_idx

    def _enter_c(self):
        if not self.visible_items: return
        sel = self.visible_items[self.selection_index]
        if isinstance(sel, str): return
        entity = sel if self.current_container else sel[0]
        if hasattr(entity, 'container') and entity.container:
            self.current_container = entity; self.selection_index = 0; self.rebuild_list()

    def _exit_c(self):
        if self.current_container:
            self.current_container = None; self.selection_index = 0; self.rebuild_list()

    def _exec(self, code):
        if not self.visible_items: return
        sel = self.visible_items[self.selection_index]
        if isinstance(sel, str): return
        item = sel if self.current_container else sel[0]
        changed = False

        if code == "+": # Equip
            if self.game.player.body.equip(item):
                if item in self.game.all_sprites: item.kill()
                if self.current_container and item in self.current_container.container.items:
                     self.current_container.container.items.remove(item)
                changed = True
        elif code == "-" or code == "d": # Remove / Drop
            if item.item.is_equipped:
                for slot, eq in self.game.player.body.slots.items():
                    if eq == item: self.game.player.body.slots[slot] = None; item.item.is_equipped = False; break
            if self.current_container and item in self.current_container.container.items:
                 self.current_container.container.items.remove(item)
            self._safe_drop(item)
            changed = True
        
        if changed: self.rebuild_list()

    def _safe_drop(self, item):
        px, py = (self.game.player.physics.x, self.game.player.physics.y) if self.game.player.physics else (1,1)
        offsets = [(0,0),(0,1),(0,-1),(1,0),(-1,0),(1,1),(-1,-1)]
        random.shuffle(offsets)
        drop_x, drop_y = px, py
        for dx, dy in offsets:
            tx, ty = int(px+dx), int(py+dy)
            if hasattr(self.game.map, "is_blocked") and not self.game.map.is_blocked(tx, ty):
                drop_x, drop_y = tx, ty; break
        
        if not hasattr(item, 'physics') or not item.physics:
            item.physics = PhysicsComponent(drop_x, drop_y, speed_mps=0)
        else:
            item.physics.x, item.physics.y = drop_x, drop_y
            item.physics.vx, item.physics.vy = 0, 0
        
        if not hasattr(item, 'pickup'): item.pickup = PickupComponent()
        if item not in self.game.all_sprites: self.game.all_sprites.add(item)

    def draw(self, screen):
        screen.fill(cn.BLACK)
        pygame.draw.rect(screen, cn.DARKGREY, (0,0,WIDTH,80))
        pygame.draw.line(screen, cn.WHITE, (0,80), (WIDTH,80), 2)
        screen.blit(self.font_status.render("Inventory", True, cn.WHITE), (10, 10))
        
        start_y = 90
        for i, entry in enumerate(self.visible_items):
            if isinstance(entry, str):
                screen.blit(self.font_header.render(entry, True, cn.LIGHTGREY), (10, start_y + i*25))
                continue
            entity = entry if self.current_container else entry[0]
            is_sel = (i == self.selection_index)
            sel_color = getattr(cn, 'SELECTION_COLOR', (60, 60, 70))
            if is_sel: pygame.draw.rect(screen, sel_color, (0, start_y + i*25, WIDTH, 25))
            screen.blit(self.font_main.render(entity.item.name, True, cn.WHITE), (30, start_y + i*25))
            
        pygame.draw.rect(screen, cn.DARKGREY, (0, HEIGHT-30, WIDTH, 30))
        screen.blit(self.font_status.render("d:Drop +/-:Wear >:Enter <:Back", True, cn.SILVER), (10, HEIGHT-22))

class PickupDirectionState(GameState):
    def enter(self):
        print("[UI] Pickup: Choose direction.")
    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            dx, dy = 0, 0
            valid = False
            if event.key == pygame.K_UP: dy = -1; valid = True
            elif event.key == pygame.K_DOWN: dy = 1; valid = True
            elif event.key == pygame.K_LEFT: dx = -1; valid = True
            elif event.key == pygame.K_RIGHT: dx = 1; valid = True
            elif event.key == pygame.K_g: valid = True
            elif event.key == pygame.K_ESCAPE: 
                self.game.state_machine.pop(); return

            if valid:
                tx = int(self.game.player.physics.x / TILESIZE) + dx
                ty = int(self.game.player.physics.y / TILESIZE) + dy
                self.game.state_machine.pop()
                self.game.state_machine.push(PickupSelectState(self.game, tx, ty))

    def draw(self, screen):
        self.game.states['roaming'].draw(screen)
        pygame.draw.rect(screen, (0,0,0), (10, 10, 300, 40))
        pygame.draw.rect(screen, cn.WHITE, (10, 10, 300, 40), 2)
        screen.blit(pygame.font.SysFont("arial", 20).render("Direction? (Arrows/G)", True, cn.WHITE), (20, 18))

class PickupSelectState(GameState):
    def __init__(self, game, tx, ty):
        super().__init__(game)
        self.tx, self.ty = tx, ty
        self.items = []
        self.selected = set()
        self.cursor = 0

    def enter(self):
        px, py = self.game.player.physics.x / TILESIZE, self.game.player.physics.y / TILESIZE
        for sprite in self.game.all_sprites:
            if hasattr(sprite, 'pickup') and hasattr(sprite, 'physics'):
                sx, sy = int(sprite.physics.x / TILESIZE), int(sprite.physics.y / TILESIZE)
                dist = ((sx - px)**2 + (sy - py)**2)**0.5
                if (sx == self.tx and sy == self.ty) or dist <= sprite.pickup.pickup_radius:
                    if sprite != self.game.player: self.items.append(sprite)
        
        if not self.items:
            print("Nothing to pick up.")
            self.game.state_machine.pop()

    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE: self.game.state_machine.pop()
            elif event.key == pygame.K_UP: self.cursor = max(0, self.cursor - 1)
            elif event.key == pygame.K_DOWN: self.cursor = min(len(self.items) - 1, self.cursor + 1)
            elif event.key == pygame.K_RIGHT: self.selected.add(self.cursor)
            elif event.key == pygame.K_LEFT and self.cursor in self.selected: self.selected.remove(self.cursor)
            elif event.key == pygame.K_RETURN: self.execute_pickup(); self.game.state_machine.pop()

    def execute_pickup(self):
        for i in self.selected:
            item = self.items[i]
            success, msg = attempt_stash_item(self.game.player, item)
            print(f"Pickup {item.item.name}: {msg}")
            if success: item.kill()

    def draw(self, screen):
        self.game.states['roaming'].draw(screen)
        bg = pygame.Rect(100, 100, 400, 300)
        pygame.draw.rect(screen, (30, 30, 30), bg)
        pygame.draw.rect(screen, (200, 200, 200), bg, 2)
        font = pygame.font.SysFont("arial", 20)
        for i, item in enumerate(self.items):
            color = cn.WHITE
            prefix = "> " if i == self.cursor else "  "
            prefix += "[+] " if i in self.selected else "[ ] "
            screen.blit(font.render(f"{prefix}{item.item.name}", True, color), (120, 120 + i * 25))