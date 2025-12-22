import pygame
from typing import Dict, List

# --- DEFAULT KEYBINDINGS ---
DEFAULT_BINDINGS: Dict[str, List[int]] = {
    # --- MOVEMENT ---
    "UP":       [pygame.K_UP, pygame.K_w, pygame.K_KP8],
    "DOWN":     [pygame.K_DOWN, pygame.K_s, pygame.K_KP2],
    "LEFT":     [pygame.K_LEFT, pygame.K_a, pygame.K_KP4],
    "RIGHT":    [pygame.K_RIGHT, pygame.K_d, pygame.K_KP6],
    "WAIT":     [pygame.K_PERIOD, pygame.K_KP5, pygame.K_KP_PERIOD],
    "JUMP":     [pygame.K_SPACE],
    "CYCLE":    [pygame.K_TAB],

    # --- INTERACTION ---
    "PICKUP":   [pygame.K_g],
    "INTERACT": [pygame.K_e],
    "AIM":      [pygame.K_f],
    "FIRE":     [pygame.K_f, pygame.K_RETURN],
    "RELOAD":   [pygame.K_r],
    "OPEN":     [pygame.K_o],
    "CLOSE":    [pygame.K_c],
    "BASH":     [pygame.K_b],
    "ZAP":      [pygame.K_z],

    # --- INVENTORY ---
    "INSPECT":        [pygame.K_i],
    "THROW":          [pygame.K_t],
    "ACTIVATE":       [pygame.K_a],
    "REFILL":         [pygame.K_r],
    "DROP":           [pygame.K_d],
    "EAT":            [pygame.K_e],
    "QUAFF":          [pygame.K_q],
    "WIELD":          [pygame.K_w],
    "WEAR":           [pygame.K_PLUS, pygame.K_KP_PLUS],
    "UNWEAR":         [pygame.K_MINUS, pygame.K_KP_MINUS],
    "ENTER_CONTAINER":[pygame.K_GREATER, pygame.K_PERIOD],
    "EXIT_CONTAINER": [pygame.K_LESS, pygame.K_COMMA],

    # --- SYSTEM ---
    "CONFIRM":  [pygame.K_RETURN, pygame.K_KP_ENTER],
    "CANCEL":   [pygame.K_ESCAPE, pygame.K_BACKSPACE],
    "MENU":     [pygame.K_ESCAPE],
    
    # --- META ---
    "SAVE":     [pygame.K_s], 
    "LOAD":     [pygame.K_l],
    "QUIT":     [pygame.K_q],
    "DEBUG_CONSOLE": [pygame.K_BACKQUOTE],
}

class InputManager:
    def __init__(self, key_bindings: Dict[str, List[int]] = None):
        self.bindings = key_bindings if key_bindings else DEFAULT_BINDINGS
        
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