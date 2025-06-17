import pygame
import os

class TextDisplay:
    def __init__(self, text, x, y, font_size=48, glow=False,read_line=None,bold=False):
        self.text = text
        self.x = x
        self.y = y
        self.font_size = font_size
        self.glow = glow
        self.bold=bold

        self.font = pygame.font.SysFont("Segoe-UI", self.font_size, bold=bold)
        self.text_color = (207, 128, 255)  # fioletowy neon
        self.glow_color = (120, 0, 170)

        self.read_line=read_line
    def draw(self, surface):
        if self.read_line is not None:
            self.update_from_file(prefix="Punkty Dante: ")
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=(self.x, self.y))

        if self.glow:
            for dx in [-2, -1, 0, 1, 2]:
                for dy in [-2, -1, 0, 1, 2]:
                    if dx != 0 or dy != 0:
                        glow_surface = self.font.render(self.text, True, self.glow_color)
                        glow_rect = glow_surface.get_rect(center=(self.x + dx, self.y + dy))
                        surface.blit(glow_surface, glow_rect.topleft)

        surface.blit(text_surface, text_rect.topleft)
    def update_from_file(self,prefix=""):
        if self.read_line is not None:
            try:
                BASE_DIR = os.path.dirname(os.path.abspath(__file__))
                file_path=os.path.join(BASE_DIR,"player_shop.txt")
                if os.path.exists(file_path):
                    with open(file_path, "r", encoding="utf-8") as f:
                        lines = f.readlines()
                    if len(lines) >= self.read_line:
                        line_value = lines[self.read_line - 1].strip()
                        self.text = f"{prefix}{line_value}"
            except Exception as e:
                print(f"Błąd podczas odczytu pliku w TextDisplay: {e}")