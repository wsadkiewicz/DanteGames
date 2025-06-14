from game_config import SCREEN_WIDTH, SCREEN_HEIGHT
from player import Player
from enemy import Enemy
from game_object import GameObject
from button import Button
from text_display import TextDisplay
from image_display import SpriteObject
import pygame
import random
import os

class Level:
    def __init__(self):
        self.walls = []
        self.players = {}
        self.enemies = []
        self.bullets = []
        self.buttons = []
        self.texts = []
        self.images = []

    def add_wall(self, wall):
        self.walls.append(wall)

    def add_player(self, player_id, player):
        self.players[player_id] = player

    def add_enemy(self, enemy):
        self.enemies.append(enemy)
    
    def add_button(self, button):
        self.buttons.append(button)

    def add_image(self, sprite):
        self.images.append(sprite)

    def update(self, delta_time, mouse_pos=None, mouse_click=False):
        for player in self.players.values():
            player.movement(delta_time, self.walls)
        for enemy in self.enemies[:]:
            if not enemy.alive:
                self.enemies.remove(enemy)
            else:
                enemy.movement(delta_time, self.walls)
                for player in self.players.values():
                    for enemy in self.enemies:
                        distance = ((player.x - enemy.x)**2 + (player.y - enemy.y)**2)**0.5
                        if distance < player.size + enemy.size:  # kolizja okręgów
                            player.take_damage()
                            if player.lives <= 0:
                                self=Level()
                                self.load_from_file("game_over.txt")
        for bullet in self.bullets:
            bullet.move(delta_time)
            bullet.check_collision(self.walls, self.players, self.enemies)
        self.bullets = [b for b in self.bullets if b.alive]
        new_level = self
        for button in self.buttons:
            if mouse_pos:
                button.update(mouse_pos)
                if button.is_clicked(mouse_pos, mouse_click) and mouse_click:
                    result = button.click(self)
                    if result:
                        new_level = result

        if not mouse_click:
            for button in self.buttons:
                button.reset_click()

        return new_level

    def load_from_file(self, filename):
        try:
            BASE_DIR = os.path.dirname(os.path.abspath(__file__))
            level_file_path = os.path.join(BASE_DIR,"levels/" + filename)
            player_stats_path = os.path.join(BASE_DIR, "player_stats.txt")

            self.add_wall(GameObject(-8000, 1500, 16000, 2000))
            self.add_wall(GameObject(-8000, -3500, 16000, 2000))
            self.add_wall(GameObject(1500, -8000, 2000, 16000))
            self.add_wall(GameObject(-3500, -8000, 2000, 16000))

            with open(level_file_path, "r") as f:
                lines = f.readlines()

            for line in lines:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue

                tokens = line.split()
                if tokens[0] == "Enemy":
                    speed = int(tokens[1])
                    max_health = int(tokens[2])
                    types = tokens[3:]
                    

                    for _ in range(100):
                        x = random.uniform(-1000, 1000)
                        y = random.uniform(-1000, 1000)
                        if abs(x) < 200 and abs(y) < 200:
                            continue

                        enemy_rect = pygame.Rect(x, y, 100, 40)
                        if any(enemy_rect.colliderect(wall.get_rect()) for wall in self.walls):
                            continue

                        direction = random.uniform(0, 360)
                        enemy = Enemy(enemy_id=10000 + len(self.enemies),enemy_type=types[0],x=x,y=y,speed=speed, direction=direction,max_health=max_health)
                        self.add_enemy(enemy)
                        break

                elif tokens[0] == "Wall" and len(tokens) == 5:
                    x, y, w, h = map(int, tokens[1:])
                    wall = GameObject(x, y, w, h)
                    self.add_wall(wall)

                elif tokens[0] == "Player":
                    with open(player_stats_path, "r") as pfile:
                        stats = [line.strip() for line in pfile.readlines()]
                        speed = int(stats[0])
                        size = int(stats[1])
                        color = eval(stats[2])
                        bullet_speed = int(stats[3])
                        power = int(stats[4])
                    player = Player(player_id=1,x=0,y=0,cam_x=0,cam_y=0,speed=speed,size=size,color=color,lives=3,bullet_speed=bullet_speed,power=power)
                    self.add_player(1, player)

                elif tokens[0] == "Button" and len(tokens) >= 6:
                    x_percent = float(tokens[1])
                    y_percent = float(tokens[2])
                    x = int(SCREEN_WIDTH * x_percent / 100)
                    y = int(SCREEN_HEIGHT * y_percent / 100)

                    width = int(tokens[3])
                    height = int(tokens[4])
                    action_type = tokens[5] if tokens[5].lower() != "none" else None
                    text = " ".join(tokens[6:]) if len(tokens) > 6 else ""

                    button = Button(x, y, width, height, text, action_type)
                    self.add_button(button)

                elif tokens[0] == "Text":
                    if len(tokens) >= 4:
                        x = int(tokens[1])
                        y = int(tokens[2])
                        text_str = " ".join(tokens[3:])
                        self.texts.append(TextDisplay(text_str, x, y))

                elif tokens[0] == "Image":
                    x = int(tokens[1])
                    y = int(tokens[2])
                    image_content = " ".join(tokens[3:])
                    image_path = os.path.join(BASE_DIR,image_content)
                    sprite = SpriteObject(image_path, x=x, y=y)
                    self.add_image(sprite)
                        

        except Exception as e:
            print(f"Błąd podczas wczytywania poziomu: {e}")

    def draw_images(self, surface):
        # Rysujemy wszystkie obrazy na ekranie (bez przesunięcia kamery)
        for sprite in self.images:
            sprite.draw(surface, cam_x=0, cam_y=0)
