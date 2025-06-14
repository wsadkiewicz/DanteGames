import pygame

pygame.init()  # Musi być wywołane przed użyciem pygame.display.Info()

# Pobierz bieżące parametry wyświetlacza
display_info = pygame.display.Info()
SCREEN_WIDTH = display_info.current_w
SCREEN_HEIGHT = display_info.current_h