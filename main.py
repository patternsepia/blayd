import sys
import os
from types import SimpleNamespace

import pygame

# Engine
from engine.events import StateManager
from engine import colors as cn
from engine.input import InputManager
# Game Logic
import game.deebee as db
from game.map_gen import Map
from game.loader import *
from game.entities import create_player, create_mob
from game.systems import CombatSystem
from game.systems import MaterialSystem
# UI & States
from game.hud import HUD
from game.states import MainMenuState, RoamingState

# Persistence
from game.persist import save_game_state, load_game_state

class Game:
    def __init__(self):
        if not os.path.exists(DATA_DIR): os.makedirs(DATA_DIR)
        pygame.init()
        pygame.display.set_caption(db.TITLE)
        
        # Settings & Config
        self.c = db.load_settings() # Assign settings to self.c for consistency
        self.cfg = SimpleNamespace(
            WIDTH = self.c["window"]["width"],
            HEIGHT = self.c["window"]["height"],
            TPS = self.c["performance"]["tps"],
            FPS =  self.c["performance"]["fps"]
        )
        self.input = InputManager() # <--- Initialize Input
        self.screen = pygame.display.set_mode((db.WIDTH, db.HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True
        self.dt = 0
        
        # Data Loading
        self.item_defs = load_item_definitions()
        self.body_plans = load_body_plans()
        self.loadout_defs = validate_loadouts(load_loadouts(), self.item_defs)
        self.material_defs = load_materials()
        
        self.hud = HUD()
        self.custom_seed = None
        
        # State Machine Initialization
        self.state_machine = StateManager(self)
        self.states = {
            'roaming': RoamingState(self),
            'menu': MainMenuState(self)
        }
        
        # Start at Main Menu
        self.state_machine.push(self.states['menu'])

        # Game Objects (Initialized later)
        self.map = None
        self.player = None
        self.all_sprites = None
        self.mobs = None
        self.combat_system = None
        self.material_sytem = MaterialSystem(self.material_defs)

    def new_game(self):
        self.map = Map(db.GRID_WIDTH, db.GRID_HEIGHT, seed=self.custom_seed)
        self.custom_seed = None
        
        self.all_sprites = pygame.sprite.Group()
        self.mobs = pygame.sprite.Group()
        
        self.player = create_player(self) 
        self.all_sprites.add(self.player)
        
        for _ in range(3):
            mob = create_mob(self)
            self.mobs.add(mob)
            self.all_sprites.add(mob)

        self.combat_system = CombatSystem()
        self.state_machine.set(self.states['roaming'])

    def save_game(self):
        save_game_state(self)

    def load_game(self):
        if load_game_state(self):
            self.state_machine.set(self.states['roaming'])

    def draw_grid(self):
        # Helper to draw grid lines (used by RoamingState)
        for x in range(0, db.WIDTH, db.TILESIZE):
            pygame.draw.line(self.screen, cn.DARKGREY, (x, 0), (x, db.HEIGHT))
        for y in range(0, db.HEIGHT, db.TILESIZE):
            pygame.draw.line(self.screen, cn.DARKGREY, (0, y), (db.WIDTH, y))

    def run(self):
        while self.running:
            self.dt = self.clock.tick(self.cfg.FPS) / 1000.0
            
            # 1. Poll Inputs
            self.input.update() # <--- Translate Keys to Actions
            
            # 2. Handle Events (Quit, Typing)
            # We still need this for window events and text typing
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                # Pass RAW events to state machine (for typing)
                self.state_machine.handle_event(event)
            
            # 3. Handle Actions (Gameplay / Menu Nav)
            # Pass PROCESSED actions to state machine
            self.state_machine.handle_input(self.input)
            
            self.state_machine.update()
            self.state_machine.draw(self.screen)
            pygame.display.flip()

if __name__ == "__main__":
    g = Game()
    g.run()
    pygame.quit()
    sys.exit()