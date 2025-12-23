import pygame
from engine import colors as cn

# UI now relies on logical actions, not specific keys
# We pass the 'input_manager' to the handle_input methods

class Widget:
    def __init__(self, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)
        self.visible = True
        self.active = True
        self.selected = False

    def handle_input(self, input_mgr):
        """Returns True if input was consumed."""
        return False

    def draw(self, surface):
        pass

class Button(Widget):
    def __init__(self, x, y, w, h, text, font, action_callback, trigger_action="CONFIRM"):
        super().__init__(x, y, w, h)
        self.text = text
        self.font = font
        self.callback = action_callback
        self.trigger_action = trigger_action # The logical action that clicks this
        
        # Style
        self.bg_color = cn.get("darkgrey")
        self.hover_color = cn.get("lightblue")
        self.text_color = cn.get("white")
        self.border_color = cn.get("lightgrey")

    def handle_input(self, input_mgr):
        if not self.active or not self.visible: return False
        
        # Mouse Click
        if pygame.mouse.get_pressed()[0]:
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                self.trigger()
                return True
        
        # Logical Action Trigger (e.g. CONFIRM)
        if self.selected and input_mgr.is_just_pressed(self.trigger_action):
            self.trigger()
            return True
            
        return False

    def trigger(self):
        if self.callback: self.callback()

    def draw(self, surface):
        if not self.visible: return
        color = self.hover_color if self.selected else self.bg_color
        if self.rect.collidepoint(pygame.mouse.get_pos()): color = self.hover_color
            
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, self.border_color, self.rect, 2)
        
        txt_surf = self.font.render(self.text, True, self.text_color)
        tx = self.rect.x + (self.rect.width - txt_surf.get_width()) // 2
        ty = self.rect.y + (self.rect.height - txt_surf.get_height()) // 2
        surface.blit(txt_surf, (tx, ty))

class VBox(Widget):
    """Vertical Container that handles selection navigation."""
    def __init__(self, x, y, w, padding=10):
        super().__init__(x, y, w, 0)
        self.padding = padding
        self.children = []
        self.selection_index = 0

    def add_child(self, widget):
        current_h = sum([c.rect.height + self.padding for c in self.children])
        widget.rect.x = self.rect.x
        widget.rect.y = self.rect.y + current_h
        if isinstance(widget, Button): widget.rect.width = self.rect.width
        self.children.append(widget)
        self.rect.height = current_h + widget.rect.height
        self._update_selection()

    def handle_input(self, input_mgr):
        if not self.visible: return False
        
        # Navigation Actions
        if input_mgr.is_just_pressed("DOWN"):
            self.selection_index = (self.selection_index + 1) % len(self.children)
            self._update_selection()
            return True
        elif input_mgr.is_just_pressed("UP"):
            self.selection_index = (self.selection_index - 1) % len(self.children)
            self._update_selection()
            return True

        # Pass to selected child
        if self.children:
            return self.children[self.selection_index].handle_input(input_mgr)
        return False

    def _update_selection(self):
        for i, child in enumerate(self.children):
            if hasattr(child, 'selected'):
                child.selected = (i == self.selection_index)

    def draw(self, surface):
        if not self.visible: return
        for child in self.children: child.draw(surface)

# InputBox remains mostly event-driven for text typing, so we keep handle_event there
class InputBox(Widget):
    def __init__(self, x, y, w, h, font, initial_text=""):
        super().__init__(x, y, w, h)
        self.text = initial_text
        self.font = font
        
    def handle_event(self, event):
        """Use RAW events for typing, InputManager for navigation."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                if len(event.unicode) > 0 and event.unicode.isprintable():
                    self.text += event.unicode
            return True
        return False
    
    # Optional stub if something calls handle_input
    def handle_input(self, input_mgr): return False

    def draw(self, surface):
        pygame.draw.rect(surface, cn.get("darkgrey"), self.rect)
        pygame.draw.rect(surface, cn.get("white"), self.rect, 2)
        txt = self.font.render(self.text, True, cn.get("white"))
        surface.blit(txt, (self.rect.x + 5, self.rect.y + 5))
    
    # Helper Label Class
class Label(Widget):
    def __init__(self, x, y, text, font, color=None):
        if color is None:
            color = cn.get("white")
        surf = font.render(text, True, color)
        super().__init__(x, y, surf.get_width(), surf.get_height())
        self.text, self.font, self.color = text, font, color
    def draw(self, surface):
        surface.blit(self.font.render(self.text, True, self.color), self.rect)