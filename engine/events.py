import pygame
import sys

class GameState:
    """Base class for all game states (Roaming, Inventory, Menus)."""
    def __init__(self, game):
        self.game = game

    def enter(self): pass
    def exit(self): pass
    def handle_input(self, event): pass
    def update(self): pass
    def draw(self, screen): pass

class StateManager:
    def __init__(self, game):
        self.game = game
        self.stack = []

    def push(self, state):
        if self.stack:
            self.stack[-1].exit() # Pause previous state
        self.stack.append(state)
        state.enter()

    def pop(self):
        if self.stack:
            exiting = self.stack.pop()
            exiting.exit()
        if self.stack:
            self.stack[-1].enter() # Resume previous state

    def set(self, state):
        """Clears stack and sets new root state."""
        while self.stack:
            self.stack.pop().exit()
        self.stack.append(state)
        state.enter()

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game.running = False
                self.game.playing = False
                return

            if self.stack:
                self.stack[-1].handle_input(event)

    def update(self):
        if self.stack:
            self.stack[-1].update()

    def draw(self, screen):
        # Draw from bottom up so backgrounds persist (e.g. Inventory over Gameplay)
        # Or just draw top if it's opaque. For simplicity, draw all:
        for state in self.stack:
            state.draw(screen)