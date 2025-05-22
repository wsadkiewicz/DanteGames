import pygame

class GameObject:
    def __init__(self, x, y, width, height, color=(0, 100, 255)):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color

    def draw(self, surface, camera_x, camera_y):
        screen_rect = self.rect.move(-camera_x, -camera_y)
        pygame.draw.rect(surface, self.color, screen_rect)

    def get_rect(self):
        return self.rect