import pygame
import sys
import math
from player import Player
from level import Level
from enemy import Enemy
from game_object import GameObject
from bullet import Bullet
from button import Button
from text_display import TextDisplay
from game_config_singleplayer import screen, font, clock, SCREEN_WIDTH, SCREEN_HEIGHT
import random
import traceback

def draw_grid(surface, cam_x, cam_y, grid_size=50):
    grid_color = (50, 0, 70)  # ciemny fioletowy

    width, height = surface.get_size()

    # przesunięcie siatki o kamerę (kam_x, cam_y)
    offset_x = cam_x % grid_size
    offset_y = cam_y % grid_size

    # pionowe linie
    for x in range(-offset_x, width, grid_size):
        pygame.draw.line(surface, grid_color, (x, 0), (x, height))

    # poziome linie
    for y in range(-offset_y, height, grid_size):
        pygame.draw.line(surface, grid_color, (0, y), (width, y))


pygame.init()
pygame.mixer.init()

player = None
level = Level()
level.load_from_file("start_menu.txt")
player = None
if level.players:
    player = level.players.get(1)
if not player:
    print("Gracz nie został wczytany z poziomu.")

try:
    running = True
    while running:

        dt = clock.tick(60) / 1000
        keys = pygame.key.get_pressed()

        if player and player.alive:
            simulated_keys = {
                "up": keys[pygame.K_w],
                "down": keys[pygame.K_s],
                "left": keys[pygame.K_a],
                "right": keys[pygame.K_d],
                "slow": keys[pygame.K_LSHIFT]
            }
            player.simulate_input(simulated_keys)

        game_events=pygame.event.get()
        for event in game_events:
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE and level.can_be_paused:
                player.lives=0

        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()[0]
        updated_level = level.update(dt, mouse_pos, mouse_click, events=game_events)
        if updated_level is not level:
            level = updated_level
            player = level.players.get(1)

        screen.fill((0, 0, 0))

        if player:
            cam_x = player.x - SCREEN_WIDTH // 2
            cam_y = player.y - SCREEN_HEIGHT // 2
            draw_grid(screen, cam_x, cam_y, grid_size=50)
        else:
            cam_x = -980
            cam_y = -980

        if level.images:
            level.draw_images(screen)

        for wall in level.walls:
            wall.draw(screen, cam_x, cam_y, draw_glow_only=True)

        for wall in level.walls:
            wall.draw(screen, cam_x, cam_y, draw_glow_only=False)

        for enemy in level.enemies:
            enemy.movement(dt, level.walls)
            enemy.draw(screen, cam_x, cam_y)

        for bullet in level.bullets:
            bullet.draw(screen, cam_x, cam_y)

        for button in level.buttons:
            button.draw(screen)

        for text in level.texts:
            text.draw(screen)

        if player and player.alive:
            player.draw(screen,cam_x,cam_y)
            player.draw_lives(screen)

        for explosion in level.explosions:
            explosion.draw(screen, cam_x, cam_y)

        for input in level.inputs:
            input.draw(screen)

        pygame.display.flip()

except Exception as e:
    print("Wystąpił błąd podczas działania gry:")
    traceback.print_exc()

finally:
    pygame.quit()
    #input("Naciśnij Enter, aby zamknąć...")
    sys.exit()