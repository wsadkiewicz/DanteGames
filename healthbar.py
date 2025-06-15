import pygame

class Healthbar:
    def __init__(self, owner, max_value, id):
        self.owner = owner
        self.ID = id
        self.max_value = max_value
        self.value = max_value

        self.width = 60
        self.height = 12
        self.offset_y = 30

    def update(self, new_value):
        self.value = max(0, min(new_value, self.max_value))

    def draw(self, surface, cam_x, cam_y):
        # Pozycja nad przeciwnikiem
        x = self.owner.rect.centerx - self.width // 2 - cam_x
        y = self.owner.rect.top - self.offset_y - cam_y

        # Tło (ciemne tło paska)
        bg_rect = pygame.Rect(x - 5, y - 5, self.width + 10, self.height + 10)
        pygame.draw.rect(surface, (0, 0, 0), bg_rect)

        # Pasek zdrowia
        health_ratio = self.value / self.max_value
        fg_width = int(self.width * health_ratio)
        fg_rect = pygame.Rect(x, y, fg_width, self.height)
        pygame.draw.rect(surface, (10, 250, 10), fg_rect)

        # Ramka
        pygame.draw.rect(surface, (0, 0, 0), bg_rect, 1)