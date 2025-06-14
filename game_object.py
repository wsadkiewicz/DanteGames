import pygame

class GameObject:
    def __init__(self, x, y, width, height, color=(0, 0, 0)):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color

    def get_rect(self):
        return self.rect

    def draw(self, surface, cam_x, cam_y, draw_glow_only=False):
        rect = self.get_rect()
        draw_rect = pygame.Rect(rect.x - cam_x, rect.y - cam_y, rect.width, rect.height)

        glow_color = (180, 0, 255)  # neon fiolet
        glow_thickness = 6

        glow_rect = pygame.Rect(draw_rect.x - glow_thickness//2,
        draw_rect.y - glow_thickness//2,
        draw_rect.width + glow_thickness,
        draw_rect.height + glow_thickness)

        if draw_glow_only:
            pygame.draw.rect(surface, glow_color, glow_rect)
        else:
            pygame.draw.rect(surface, self.color, draw_rect)