import pygame
import os
pygame.init()  # Musi być wywołane przed użyciem pygame.display.Info()

# Pobierz bieżące parametry wyświetlacza
display_info = pygame.display.Info()
SCREEN_WIDTH = display_info.current_w
SCREEN_HEIGHT = display_info.current_h
BASE_DIR_NAME = os.path.dirname(os.path.abspath(__file__))
sound_laser_shot=pygame.mixer.Sound(BASE_DIR_NAME+"/assets/laser_shot_short.mp3")
sound_explosive_shot=pygame.mixer.Sound(BASE_DIR_NAME+"/assets/explosive_shot.mp3")
sound_hurt=pygame.mixer.Sound(BASE_DIR_NAME+"/assets/hurt.mp3")
sound_explosion=pygame.mixer.Sound(BASE_DIR_NAME+"/assets/explosion.mp3")
sound_click=pygame.mixer.Sound(BASE_DIR_NAME+"/assets/click.mp3")
sound_hover=pygame.mixer.Sound(BASE_DIR_NAME+"/assets/hover.mp3")
sound_click.set_volume(0.5)
sound_laser_weaker=sound_laser_shot
sound_laser_weaker.set_volume(0.4)
Sounds=[sound_laser_shot,sound_explosive_shot,sound_explosion,sound_hurt,sound_laser_weaker,sound_click,sound_hover]