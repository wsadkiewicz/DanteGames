import pygame
import os

class InputBox:
    def __init__(self, x, y, width, height, send_to_file, send_to_line, type=1,clear_self=True):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.type = type
        self.text = ""
        self.active = False
        self.font = pygame.font.SysFont("Segoe UI", 30)
        self.clear_self=clear_self
        self.hovered=False
        self.scale_factor=1.0
        self.rescale_offset=1.0

        self.base_rect = pygame.Rect(0, 0, width, height)
        self.base_rect.center = (x, y)

        self.text_color_default = (211, 100, 255)  # jasnofioletowy
        self.text_color_error = (255, 0, 0)      # czerwony
        self.current_color = self.text_color_default

        # Załaduj i przeskaluj obraz
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(BASE_DIR, "assets/input.png")
        self.send_to_file = os.path.join(BASE_DIR,send_to_file)
        self.send_to_line = send_to_line
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.smoothscale(self.image, (width, height))

        # Oblicz prostokąt centrowany względem x, y
        self.rect = self.image.get_rect(center=(x, y))

    def draw(self, surface):
        surface.blit(self.image, self.rect.topleft)
        txt_surface = self.font.render(self.text, True, self.current_color)
        text_rect = txt_surface.get_rect(center=self.rect.center)
        surface.blit(txt_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = True
                self.current_color = self.text_color_default
            else:
                if self.active and self.text.strip() != "":
                    if self.check():
                        self.send()
                self.active = False

        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                if self.text.strip() != "" and self.check():
                    self.send()
                    self.active = False
            else:
                self.text += event.unicode

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
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(BASE_DIR, "assets/input_hover.png")
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.smoothscale(self.image, (self.width, self.height))

    def _reset_hover_effect(self):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(BASE_DIR, "assets/input.png")
        self.image = pygame.image.load(image_path).convert_alpha()
        self.image = pygame.transform.smoothscale(self.image, (self.width, self.height))
        

    def check(self):
        if self.type == 1:
            return True
        elif self.type == 2:  # Nowy typ: kolor HEX
            text = self.text.strip()
            if len(text) == 7 and text.startswith("#"):
                try:
                    int(text[1:], 16)  # sprawdzamy, czy pozostałe znaki to poprawny hex
                    return True
                except ValueError:
                    pass
            self.current_color = self.text_color_error
            return False
        elif self.type == 3:  # INT only
            text = self.text.strip()
            try:
                int(text)
                with open(self.send_to_file, 'r', encoding='utf-8') as file:
                    lines = file.readlines()
                current=int(lines[0])
                highest=int(lines[1])
                self.current_color = self.text_color_default
                if current > highest:
                    self.current_color = self.text_color_error
                return True
            except ValueError:
                self.current_color = self.text_color_error
                return False

    def send(self):
        try:
            if not os.path.exists(self.send_to_file):
                lines = []
            else:
                with open(self.send_to_file, 'r', encoding='utf-8') as file:
                    lines = file.readlines()

            while len(lines) < self.send_to_line:
                lines.append("\n")

            value_to_write = self.text

            if self.type == 2:
                hex_color = self.text.strip()
                r = int(hex_color[1:3], 16)
                g = int(hex_color[3:5], 16)
                b = int(hex_color[5:7], 16)
                value_to_write = f"({r},{g},{b})"

            lines[self.send_to_line - 1] = value_to_write + "\n"

            with open(self.send_to_file, 'w', encoding='utf-8') as file:
                file.writelines(lines)

        except Exception as e:
            print(f"Błąd zapisu do pliku: {e}")

        if self.clear_self:
            self.text = ""
        if self.type==3:
            self.check()