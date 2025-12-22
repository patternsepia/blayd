import pygame
from game.deebee import TILESIZE

class Entity(pygame.sprite.Sprite):
    def __init__(self, game_context, x=None, y=None):
        super().__init__()
        self.game = game_context
        
        # Generic Transform Data
        if x is not None and y is not None:
            self.pos_x = x * TILESIZE
            self.pos_y = y * TILESIZE
        else:
            self.pos_x = 0
            self.pos_y = 0
        
        self.visual = None
        self.physics = None
        self.stats = None
        self.control = None

        self.item = None
        self.container = None

        self.body = None
        
        # --- ENGINE FIX: Default Placeholders ---
        # Initialize empty defaults so Pygame doesn't crash if we draw
        # before the first update cycle.
        self.image = pygame.Surface((0, 0)) # Invisible 0x0 surface
        self.rect = self.image.get_rect()

    def update(self, dt):
        # Update components in specific order
        # Pass dt (delta time) to components that need it (like Physics)
        if self.control: self.control.update(self, self.game, dt)
        if self.physics: self.physics.update(self, self.game, dt)
        if self.visual: 
            self.visual.update(self, self.game, dt)
            # Sync Pygame Sprite basics automatically
            self.image = self.visual.image
            self.rect = self.visual.rect
            
    # Call this after attaching components if you need to draw immediately
    def refresh_visuals(self):
        if self.visual:
            self.image = self.visual.image
            self.rect = self.visual.rect
            # Force position sync
            self.rect.x = int(self.pos_x)
            self.rect.y = int(self.pos_y)
    
    def cfg_control(self, ctrl):
        self.control = ctrl