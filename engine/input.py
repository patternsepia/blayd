import pygame

# --- DEFAULT KEYBINDINGS ---
# Maps logical Game Actions to Physical Keys.
# Supports multiple keys per action.

DEFAULT_BINDINGS = {
    # --- MOVEMENT ---
    "UP":       [pygame.K_UP, pygame.K_w, pygame.K_KP8],
    "DOWN":     [pygame.K_DOWN, pygame.K_s, pygame.K_KP2],
    "LEFT":     [pygame.K_LEFT, pygame.K_a, pygame.K_KP4],
    "RIGHT":    [pygame.K_RIGHT, pygame.K_d, pygame.K_KP6],
    "WAIT":     [pygame.K_PERIOD, pygame.K_KP5, pygame.K_KP_PERIOD], # Skip turn
    "JUMP":     [pygame.K_SPACE], # Jump
    "CYCLE":    [pygame.K_TAB], # Cycle through movement modes

    # --- INTERACTION & GAMEPLAY ---
    "PICKUP":   [pygame.K_g],
    "INTERACT": [pygame.K_e],                  # Doors, talking
    "AIM":      [pygame.K_f],                  # Ranged mode trigger
    "FIRE":     [pygame.K_f, pygame.K_RETURN], # Aim
    "RELOAD":   [pygame.K_r],
    "OPEN":     [pygame.K_o],
    "CLOSE":    [pygame.K_c],
    "BASH":     [pygame.K_b],
    "ZAP":      [pygame.K_z], # aim magic
    

    # --- INVENTORY MANAGEMENT ---
    # These match the hints in your InventoryUI
    "INSPECT":        [pygame.K_i],
    "THROW":          [pygame.K_t], # throw 1 unit in stack
    "ACTIVATE":       [pygame.K_a],
    "REFILL":         [pygame.K_r], # refill, reload, refuel
    "DROP":           [pygame.K_d], # drop 1 unit in stack at feet
    "EAT":            [pygame.K_e], # eat 1 unit in stack
    "QUAFF":          [pygame.K_q], # drink 1 unit in stack
    "WIELD":          [pygame.K_w],
    "WEAR":           [pygame.K_PLUS],    # + to wear
    "UNWEAR":         [pygame.K_MINUS],   # - to remove
    "ENTER_CONTAINER":[pygame.K_GREATER], # > to enter
    "EXIT_CONTAINER": [pygame.K_LESS],    # < to exit

    # --- SYSTEM / UI ---
    "CONFIRM":  [pygame.K_RETURN, pygame.K_KP_ENTER],
    "CANCEL":   [pygame.K_ESCAPE, pygame.K_BACKSPACE],
    "MENU":     [pygame.K_ESCAPE],
    
    # --- META (Save/Load) ---
    "SAVE":     [pygame.K_s], 
    "LOAD":     [pygame.K_l],
    "QUIT":     [pygame.K_q],
    
    # --- DEBUG / DEV ---
    "DEBUG_CONSOLE": [pygame.K_BACKQUOTE], # ` key
}

class InputManager:
    def __init__(self, key_bindings=None):
        self.bindings = key_bindings if key_bindings else DEFAULT_BINDINGS
        
        # State tracking
        self.actions = {action: False for action in self.bindings}
        self.just_pressed = {action: False for action in self.bindings}
        
    def update(self):
        """
        Polls hardware state. Call this once per frame in main loop.
        """
        keys = pygame.key.get_pressed()
        mods = pygame.key.get_mods()
        
        for action, key_list in self.bindings.items():
            is_active = False
            for key in key_list:
                # Special handling for Shift-keys (like < > +) could go here,
                # but generally Pygame handles keycodes distinct from modifiers.
                if keys[key]:
                    is_active = True
                    break
            
            # Update "Just Pressed" state (Rising Edge)
            if is_active and not self.actions[action]:
                self.just_pressed[action] = True
            else:
                self.just_pressed[action] = False
                
            self.actions[action] = is_active

    def is_pressed(self, action):
        """Held down (e.g. running, charging bow)."""
        return self.actions.get(action, False)

    def is_just_pressed(self, action):
        """Pressed this frame (e.g. menu navigation, firing single shot)."""
        return self.just_pressed.get(action, False)
        
    def remap(self, action, new_key_list):
        """Runtime remapping support."""
        if action in self.bindings:
            self.bindings[action] = new_key_list