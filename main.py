import sys
import os
from types import SimpleNamespace
import logging

import pygame

# Engine
from engine.events import StateManager, EventBus
from engine import colors as cn
from engine.input import InputManager
from game.logger import init_logger
# Game Logic
import game.deebee as db

from game.map_gen import Map
from game.loader import *
from game.systems import *
# UI & States
from game.hud import HUD
from game.states import MainMenuState, RoamingState
# Persistence
from game.persist import save_game_state, load_game_state

# Redirects stdout and stderr to a file
sys.stdout = open('output.log', 'w')
sys.stderr = sys.stdout

class Game:
    def __init__(self):
        # 1. Setup Logging
        init_logger(db.LOG_CONFIG)
        self.logger = logging.getLogger("Main")
        self.logger.info("--- Game Init Start ---")

        if not os.path.exists(DATA_DIR): os.makedirs(DATA_DIR)
        pygame.init()
        self.logger.info("Pygame Initialized")
        pygame.display.set_caption(db.TITLE)
        
        # Settings & Config
        self.c = db.load_settings() # Assign settings to self.c for consistency
        self.logger.info(f"Settings Loaded: {list(self.c.keys())}")
        self.cfg = SimpleNamespace(
            WIDTH = self.c["window"]["width"],
            HEIGHT = self.c["window"]["height"],
            TPS = self.c["performance"]["tps"],
            FPS =  self.c["performance"]["fps"]
        )
        self.logger.info(f"Config: {self.cfg}")
        self.input = InputManager(db.KEY_BINDINGS) # <--- Initialize Input
        self.screen = pygame.display.set_mode((db.WIDTH, db.HEIGHT))
        self.logger.info(f"Screen Created {db.WIDTH}x{db.HEIGHT}")
        self.clock = pygame.time.Clock()
        self.running = True
        self.dt = 0
        
        # Data Loading
        self.logger.info("Loading Data...")
        self.item_defs = load_items()
        self.body_plans = load_body_plans()
        self.loadout_defs = validate_loadouts(load_loadouts(), self.item_defs)
        self.material_defs = load_materials()
        self.mob_defs = load_mobs()
        self.logger.info("Data Loaded")
        
        self.hud = HUD()
        self.custom_seed = None
        
        # State Machine Initialization
        self.state_machine = StateManager(self)
        self.states = {
            'roaming': RoamingState(self),
            'menu': MainMenuState(self)
        }
        
        # Start at Main Menu
        self.logger.info("Pushing Main Menu")
        self.state_machine.push(self.states['menu'])

        # Game Objects (Initialized later)
        self.map = None
        self.player = None
        self.all_sprites = None
        self.mobs = None
        self.combat_system = None
        self.material_system = None
        self.spawner_system = None
        self.logger.info("Init Complete")


    def new_game(self):
        self.map = Map(db.GRID_WIDTH, db.GRID_HEIGHT, seed=self.custom_seed)
        self.custom_seed = None

        self.bus = EventBus()
        
        self.all_sprites = pygame.sprite.Group()
        self.mobs = pygame.sprite.Group()
        
        # Initialize systems BEFORE using them
        self.combat_system = CombatSystem()
        self.material_system = MaterialSystem(self.material_defs)
        self.spawner_system = SpawnerSystem()
        
        # Now it is safe to spawn entities
        self.spawner_system.spawn_player(self)
        self.spawner_system.spawn_mob(self, "goblin", count=1)
        self.spawner_system.spawn_mob(self, "rat", count=3)

        self.state_machine.set(self.states['roaming'])

    def save_game(self):
        save_game_state(self)

    def load_game(self):
        if load_game_state(self):
            self.state_machine.set(self.states['roaming'])

    def draw_grid(self):
        # Helper to draw grid lines (used by RoamingState)
        for x in range(0, db.WIDTH, db.TILESIZE):
            pygame.draw.line(self.screen, cn.get("darkgrey"), (x, 0), (x, db.HEIGHT))
        for y in range(0, db.HEIGHT, db.TILESIZE):
            pygame.draw.line(self.screen, cn.get("darkgrey"), (0, y), (db.WIDTH, y))

    def run(self):
        self.logger.info("Entering Run Loop")
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
            
            # System Updates (Run these regardless of State, or inside RoamingState)
            if self.state_machine.stack and isinstance(self.state_machine.stack[-1], self.states['roaming'].__class__):
                 self.material_system.update(self, self.dt) # Pass 'self' as game_context
            
            self.state_machine.draw(self.screen)
            pygame.display.flip()

if __name__ == "__main__":
    g = Game()
    g.run()
    pygame.quit()
    sys.exit()