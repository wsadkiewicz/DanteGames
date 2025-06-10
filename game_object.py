import pygame

class GameObject:
    def __init__(self, x, y, width, height, color=(0, 100, 255)):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color

    def get_rect(self):
        return self.rect