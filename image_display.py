import pygame

class SpriteObject:
    def __init__(self, image_path, x=0, y=0):
        self.image = pygame.image.load(image_path).convert_alpha()
        self.rect = self.image.get_rect(center=(x, y))
        self.x = x
        self.y = y

    def draw(self, surface, cam_x=0, cam_y=0):
        # Przesuwamy pozycję kamery
        screen_x = self.rect.centerx - cam_x
        screen_y = self.rect.centery - cam_y
        draw_rect = self.image.get_rect(center=(screen_x, screen_y))
        surface.blit(self.image, draw_rect.topleft)

    def set_position(self, x, y):
        self.x = x
        self.y = y
        self.rect.center = (x, y)

    def get_rect(self):
        self.rect.center = (self.x, self.y)
        return self.rect