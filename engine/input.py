import pygame
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

# --- DEFAULT KEYBINDINGS ---

class InputManager:
    def __init__(self, key_bindings: Dict[str, List[int]] = None):
        self.bindings = key_bindings if key_bindings else {}
        logger.info(f"InputManager initialized with {len(self.bindings)} actions.")
        
        # State tracking
        self.actions: Dict[str, bool] = {action: False for action in self.bindings}
        self.just_pressed: Dict[str, bool] = {action: False for action in self.bindings}
        
    def update(self):
        """
        Polls hardware state. Call this once per frame in main loop.
        """
        keys = pygame.key.get_pressed()
        
        for action, key_list in self.bindings.items():
            is_active = False
            for key in key_list:
                # Ensure key is within valid range to prevent IndexError
                if key < len(keys) and keys[key]:
                    is_active = True
                    break
            
            # Update "Just Pressed" state (Rising Edge)
            if is_active and not self.actions.get(action, False):
                self.just_pressed[action] = True
            else:
                self.just_pressed[action] = False
                
            self.actions[action] = is_active

    def is_pressed(self, action: str) -> bool:
        """Held down (e.g. running, charging bow)."""
        return self.actions.get(action, False)

    def is_just_pressed(self, action: str) -> bool:
        """Pressed this frame (e.g. menu navigation, firing single shot)."""
        return self.just_pressed.get(action, False)
        
    def remap(self, action: str, new_key_list: List[int]):
        """Runtime remapping support."""
        if action in self.bindings:
            self.bindings[action] = new_key_list