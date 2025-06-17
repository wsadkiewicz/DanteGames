import pygame
import os
from game_config import Sounds
pygame.init()

info = pygame.display.Info()
SCREEN_WIDTH, SCREEN_HEIGHT = info.current_w, info.current_h
BASE_DIR_NAME = os.path.dirname(os.path.abspath(__file__))

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
#pygame.display.set_caption("Singleplayer Mode")

font = pygame.font.SysFont(None, 36)
clock = pygame.time.Clock()