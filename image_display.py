import pygame

class SpriteObject:
    def __init__(self, image_path, x=0, y=0):
        self.x = x
        self.y = y
        self.image = pygame.image.load(image_path).convert_alpha()
        self.rect = self.image.get_rect(topleft=(x, y))

    def draw(self, surface, cam_x=0, cam_y=0):
        # Obliczamy pozycję na ekranie uwzględniając przesunięcie kamery
        screen_x = self.x - cam_x
        screen_y = self.y - cam_y
        surface.blit(self.image, (screen_x, screen_y))

    def set_position(self, x, y):
        self.x = x
        self.y = y
        self.rect.topleft = (x, y)

    def get_rect(self):
        # Aktualizujemy rect na podstawie pozycji
        self.rect.topleft = (self.x, self.y)
        return self.rect