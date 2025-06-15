import pygame

class TextDisplay:
    def __init__(self, text, x, y, font_size=48, glow=True):
        self.text = text
        self.x = x
        self.y = y
        self.font_size = font_size
        self.glow = glow

        self.font = pygame.font.SysFont("arial", self.font_size, bold=True)
        self.text_color = (180, 0, 255)  # fioletowy neon
        self.glow_color = (120, 0, 200)

    def draw(self, surface):
        text_surface = self.font.render(self.text, True, self.text_color)

        if self.glow:
            for dx in [-2, -1, 0, 1, 2]:
                for dy in [-2, -1, 0, 1, 2]:
                    if dx != 0 or dy != 0:
                        glow_surface = self.font.render(self.text, True, self.glow_color)
                        surface.blit(glow_surface, (self.x + dx, self.y + dy))

        surface.blit(text_surface, (self.x, self.y))