import pygame
import sys
from game_config import screen, clock
from level import Level
from player import Player
from game_object import GameObject

# Tworzenie instancji poziomu
level = Level()


# Dodajemy kilka ścian
level.add_wall(GameObject(200, 200, 300, 50))
level.add_wall(GameObject(-400, 100, 150, 150))
level.add_wall(GameObject(600, 400, 100, 300))

# Główna pętla gry
running = True
while running:
    delta_time = clock.tick(60) / 1000  # czas w sekundach

    for event in pygame.event.get():
        if event.type == pygame.QUIT or (
            event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
        ):
            running = False

    level.update(delta_time)
    level.draw(screen, 0)  # Rysujemy z perspektywy pierwszego gracza

    pygame.display.flip()

pygame.quit()
sys.exit()