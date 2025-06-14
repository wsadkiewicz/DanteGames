import pygame

class Button:
    def __init__(self, x, y, width, height, text, action_type=None, font=None, base_color=(70, 70, 70), hover_color=(100, 100, 100), text_color=(255, 255, 255)):
        self.base_rect = pygame.Rect(x, y, width, height)
        self.current_rect = self.base_rect.copy()
        self.text = text
        self.action_type = action_type
        self.base_color = base_color
        self.hover_color = hover_color
        self.text_color = text_color
        self.font = font or pygame.font.SysFont(None, 36)
        self.hovered = False
        self.scale_factor = 1.05
        self.was_pressed = False

    def draw(self, screen):
        color = self.hover_color if self.hovered else self.base_color
        pygame.draw.rect(screen, color, self.current_rect, border_radius=8)

        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.current_rect.center)
        screen.blit(text_surface, text_rect)

    def update(self, mouse_pos):
        if self.base_rect.collidepoint(mouse_pos):
            if not self.hovered:
                self.hovered = True
                self._apply_hover_effect()
        else:
            if self.hovered:
                self.hovered = False
                self._reset_hover_effect()

    def _apply_hover_effect(self):
        cx, cy = self.base_rect.center
        new_width = int(self.base_rect.width * self.scale_factor)
        new_height = int(self.base_rect.height * self.scale_factor)
        self.current_rect = pygame.Rect(0, 0, new_width, new_height)
        self.current_rect.center = (cx, cy)

    def _reset_hover_effect(self):
        self.current_rect = self.base_rect.copy()

    def is_clicked(self, mouse_pos, mouse_click):
        if self.current_rect.collidepoint(mouse_pos):
            if mouse_click and not self.was_pressed:
                self.was_pressed = True
                return True
        return False

    def reset_click(self):
        self.was_pressed = False

    def click(self, level):
        if self.action_type:
            print(f"Przycisk kliknięty. Typ akcji: {self.action_type}")
            if self.action_type.startswith("load-"):
                from level import Level
                level_name = self.action_type[len("load-"):]
                new_level = Level()
                new_level.load_from_file(f"{level_name}.txt")
                return new_level
        else:
            print("Przycisk kliknięty, ale brak działania.")
        return level