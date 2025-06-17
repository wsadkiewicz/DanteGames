from game_config import SCREEN_WIDTH, SCREEN_HEIGHT, Sounds
from player import Player
from enemy import Enemy
from game_object import GameObject
from button import Button
from explosion import Explosion
from text_display import TextDisplay
from image_display import SpriteObject
from text_input import InputBox
import pygame
import random
import os

class Level:
    def __init__(self,is_menu=False):
        self.walls = []
        self.players = {}
        self.enemies = []
        self.bullets = []
        self.buttons = []
        self.texts = []
        self.images = []
        self.explosions = []
        self.inputs = []
        self.can_be_paused = False

        self.multiplayer = False

        self.is_menu=is_menu
        self.ricochet_unlocked=False
        self.explosive_unlocked=False
        self.homing_unlocked=False

    def defeat(self):
        print("Gracz poległ")
        self.texts.append(TextDisplay(text="Defeat",x=SCREEN_WIDTH//2,y=SCREEN_HEIGHT//4,font_size=72))
        self.can_be_paused=False
        self.buttons.append(Button(x=SCREEN_WIDTH//2+150,y=int(SCREEN_HEIGHT/1.5),width=150,height=50,text="Quit",action_type="quit",type=1))
        self.buttons.append(Button(x=SCREEN_WIDTH//2-150,y=int(SCREEN_HEIGHT/1.5),width=150,height=50,text="Upgrades",action_type="load-lobby2",type=1))
    def victory(self):
        self.can_be_paused=False
        print("Gracz ukończył poziom")
        BASE_DIR2 = os.path.dirname(os.path.abspath(__file__))
        launcher = os.path.join(BASE_DIR2,"launch_level.txt")
        with open(launcher, "r", encoding="utf-8") as f:
            launches = f.readlines()
        highscore=int(launches[1])
        current=int(launches[0])
        if current == highscore:
            highscore += 1
            launches[1]=f"{highscore}"
            with open(launcher, "w", encoding="utf-8") as f:
                f.writelines(launches)
        self.texts.append(TextDisplay(text="Victory",x=SCREEN_WIDTH//2,y=SCREEN_HEIGHT//4,font_size=72))
        self.buttons.append(Button(x=SCREEN_WIDTH//2+150,y=int(SCREEN_HEIGHT/1.5),width=150,height=50,text="Quit",action_type="quit",type=1))
        self.buttons.append(Button(x=SCREEN_WIDTH//2-150,y=int(SCREEN_HEIGHT/1.5),width=150,height=50,text="Upgrades",action_type="load-lobby2",type=1))

    def add_input(self, input_box):
        self.inputs.append(input_box)

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

    def update(self, delta_time, mouse_pos=None, mouse_click=False, events=None):

        if events:
            for event in events:
                for input_box in self.inputs:
                    input_box.handle_event(event)

        for player in self.players.values():
            if player.alive:
                player.movement(delta_time, self.walls, self.bullets, mouse_pos, mouse_click)
                if player.shoot_delay > 0:
                    player.shoot_delay -= delta_time
                    if player.shoot_delay < 0:
                        player.shoot_delay = 0
        for enemy in self.enemies[:]:
            if not enemy.alive:
                self.explosions.append(Explosion(enemy.x,enemy.y,60,0.5,0,None))
                Sounds[3].play()
                self.enemies.remove(enemy)
                if not self.enemies:
                    self.bullets=[]
                    self.victory()
            else:
                enemy.movement(delta_time, self.walls, self.players)
                enemy.try_shoot_nearest_player(self.players, self.bullets)
                for player in self.players.values():
                    if player.lives <= 0 and player.alive:
                        player.alive=False
                        self.bullets=[Bullet for Bullet in self.bullets if Bullet.owner != player.player_id]
                        if not self.multiplayer:
                            self.explosions.append(Explosion(player.x,player.y,200,0.5,0,None))
                            Sounds[3].play()
                            self.defeat()
                        else:
                            pass

                    for enemy in self.enemies:
                        distance = ((player.x - enemy.x)**2 + (player.y - enemy.y)**2)**0.5
                        if distance < player.size + enemy.size:  # kolizja okręgów
                            player.take_damage()

        for bullet in self.bullets:
            bullet.move(delta_time,walls=self.walls,players=self.players,enemies=self.enemies)
            bullet.check_collision(self.walls, self.players, self.enemies, self.explosions)
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

        for explosion in self.explosions[:]:
            explosion.update(delta_time)
            if not explosion.alive:
                self.explosions.remove(explosion)

        for input in self.inputs:
            if mouse_pos:
                input.update(mouse_pos)

        return new_level

    def load_from_file(self, filename):
        try:
            BASE_DIR = os.path.dirname(os.path.abspath(__file__))
            level_file_path = os.path.join(BASE_DIR,"levels/" + filename)
            player_stats_path = os.path.join(BASE_DIR, "player_stats.txt")
            print("Wczytuję plik...")
            self.add_wall(GameObject(-8000, 1500, 16000, 2000))
            self.add_wall(GameObject(-8000, -3500, 16000, 2000))
            self.add_wall(GameObject(1500, -8000, 2000, 16000))
            self.add_wall(GameObject(-3500, -8000, 2000, 16000))
            self.can_be_paused=False
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
                        bullet_type_line = stats[5].strip()
                        bullet_type = bullet_type_line.split()
                        lives = int(stats[6])
                    player = Player(player_id=1,x=0,y=0,cam_x=0,cam_y=0,speed=speed,size=size,color=color,lives=lives,bullet_speed=bullet_speed,power=power,bullet_type=bullet_type)
                    self.add_player(1, player)
                    self.can_be_paused=True

                elif tokens[0] == "Menu":
                    self.is_menu=True
                    with open(player_stats_path, "r") as pfile:
                        stats = [line.strip() for line in pfile.readlines()]
                        bullet_type_line = stats[7].strip()
                        bullet_type = bullet_type_line.split()
                        if "ricochet" in bullet_type:
                            self.ricochet_unlocked=True
                        if "explosive" in bullet_type:
                            self.explosive_unlocked=True
                        if "homing" in bullet_type:
                            self.homing_unlocked=True

                elif tokens[0] == "Button" and len(tokens) >= 6:
                    x_percent = float(tokens[1])
                    y_percent = float(tokens[2])
                    x = int(SCREEN_WIDTH * x_percent / 100)
                    y = int(SCREEN_HEIGHT * y_percent / 100)

                    width = int(tokens[3])
                    height = int(tokens[4])
                    type = int(tokens[5])
                    action_type = tokens[6] if tokens[6].lower() != "none" else None
                    text = " ".join(tokens[7:]) if len(tokens) > 7 else ""

                    button = Button(x=x,y=y,width=width,height=height,text=text,action_type=action_type,type=type)
                    self.add_button(button)

                elif tokens[0] == "Text":
                    if len(tokens) >= 4:
                        x_percent = float(tokens[1])
                        y_percent = float(tokens[2])
                        x = int(SCREEN_WIDTH * x_percent / 100)
                        y = int(SCREEN_HEIGHT * y_percent / 100)
                        reader=int(tokens[3]) if tokens[3].lower() != "none" else None
                        text_str = " ".join(tokens[4:])
                        self.texts.append(TextDisplay(text_str, x, y, read_line=reader))

                elif tokens[0] == "Image":
                    x_percent = float(tokens[1])
                    y_percent = float(tokens[2])
                    x = int(SCREEN_WIDTH * x_percent / 100)
                    y = int(SCREEN_HEIGHT * y_percent / 100)
                    image_content = " ".join(tokens[3:])
                    image_path = os.path.join(BASE_DIR,image_content)
                    sprite = SpriteObject(image_path, x=x, y=y)
                    self.add_image(sprite)

                elif tokens[0] == "Input" and len(tokens) == 9:
                    x_percent = float(tokens[1])
                    y_percent = float(tokens[2])
                    width = int(tokens[3])
                    height = int(tokens[4])
                    input_type = int(tokens[5])
                    line = int(tokens[6])
                    filename = tokens[7]
                    clear_self = tokens[8].lower() in ["true"]

                    x = int(SCREEN_WIDTH * x_percent / 100)
                    y = int(SCREEN_HEIGHT * y_percent / 100)

                    input_box = InputBox(x=x, y=y, width=width, height=height,send_to_file=filename, send_to_line=line, type=input_type, clear_self=clear_self)
                    self.add_input(input_box)

                elif tokens[0] == "Music":
                    track = tokens[1]
                    pygame.mixer.music.load(os.path.join(BASE_DIR, "assets/"+track))
                    pygame.mixer.music.play(-1,fade_ms=1000)
                    
                elif tokens[0] == "Display":
                    with open(player_stats_path, "r") as pfile:
                        stats = [line.strip() for line in pfile.readlines()]
                        color = eval(stats[2])
                    x_percent=float(tokens[1])
                    y_percent=float(tokens[2])
                    x = int(SCREEN_WIDTH * x_percent / 100) - 980
                    y = int(SCREEN_HEIGHT * y_percent / 100) - 980
                    enemy = Enemy(enemy_id=9885,enemy_type="display",x=x,y=y,speed=0, direction=0,max_health=1,color=color)
                    self.add_enemy(enemy)
                        

        except Exception as e:
            print(f"Błąd podczas wczytywania poziomu: {e}")

    def draw_images(self, surface):
        # Rysujemy wszystkie obrazy na ekranie (bez przesunięcia kamery)
        for sprite in self.images:
            sprite.draw(surface, cam_x=0, cam_y=0)