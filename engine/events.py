import pygame
import sys
from typing import List, Optional

class Signal:
    """
    A specific channel that subscribers can listen to.
    """
    def __init__(self):
        self._subscribers = []

    def connect(self, func):
        """Adds a function to be called when this signal emits."""
        if func not in self._subscribers:
            self._subscribers.append(func)

    def disconnect(self, func):
        if func in self._subscribers:
            self._subscribers.remove(func)

    def emit(self, data=None):
        """Calls all connected subscribers with the provided data."""
        for func in self._subscribers:
            func(data)

class EventBus:
    """
    The central hub for global game events.
    """
    def __init__(self):
        self.signals = {}

    def subscribe(self, topic: str, func):
        """
        Listens for a specific topic string (e.g., "mob_killed").
        Creates the Signal automatically if it doesn't exist.
        """
        if topic not in self.signals:
            self.signals[topic] = Signal()
        self.signals[topic].connect(func)

    def unsubscribe(self, topic: str, func):
        if topic in self.signals:
            self.signals[topic].disconnect(func)

    def emit(self, topic: str, data=None):
        """
        Broadcasts an event to all subscribers of 'topic'.
        """
        if topic in self.signals:
            self.signals[topic].emit(data)
        # Optional: Debug log
        print(f"[EventBus] Emitted '{topic}' with payload: {data}")

class GameState:
    """
    Base class for all game states (Roaming, Inventory, Menus).
    """
    def __init__(self, game):
        self.game = game

    def enter(self): 
        """Called when state becomes active."""
        pass
        
    def exit(self): 
        """Called when state is popped or paused."""
        pass
        
    def handle_input(self, event: pygame.event.Event): 
        """Handle raw Pygame events."""
        pass
        
    def update(self): 
        """Per-frame logic update."""
        pass
        
    def draw(self, screen: pygame.Surface): 
        """Render to the screen."""
        pass

class StateManager:
    def __init__(self, game):
        self.game = game
        self.stack: List[GameState] = []

    def push(self, state: GameState):
        """Pauses current state and enters new state."""
        if self.stack:
            self.stack[-1].exit()
        self.stack.append(state)
        state.enter()

    def pop(self):
        """Exits current state and resumes previous."""
        if self.stack:
            exiting = self.stack.pop()
            exiting.exit()
        if self.stack:
            self.stack[-1].enter()

    def set(self, state: GameState):
        """Clears stack and sets new root state."""
        while self.stack:
            self.stack.pop().exit()
        self.stack.append(state)
        state.enter()

    def handle_input(self, input_mgr):
        if self.stack:
            self.stack[-1].handle_input(input_mgr)
                
    def handle_event(self, event):
        if self.stack:
            # Assumes the State class also has a handle_event method
            if hasattr(self.stack[-1], 'handle_event'):
                self.stack[-1].handle_event(event)

    def update(self):
        if self.stack:
            self.stack[-1].update()

    def draw(self, screen: pygame.Surface):
        # Draw from bottom up so backgrounds persist
        for state in self.stack:
            state.draw(screen)