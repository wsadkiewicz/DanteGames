import pygame
import math
from healthbar import Healthbar
import time
import random
from game_config import BASE_DIR_NAME, Sounds

class Enemy:
    def __init__(self, enemy_id, enemy_type="default", x=0, y=0, speed=3, direction=0,max_health=100,shoot_cooldown=1.0,color=(30,30,30)):
        self.enemy_id = enemy_id
        self.enemy_type = enemy_type
        self.x = x
        self.y = y
        self.speed = speed
        self.direction = direction  # kąt w stopniach (0-359)
        self.size = 25
        self.max_health = max_health
        self.health = self.max_health
        self.healthbar = Healthbar(self, self.max_health, self.enemy_id)
        self.alive=True
        self.last_shot_time = 0
        self.shoot_cooldown = shoot_cooldown
        self.second_attack_delay = 0
        self.second_shoot_time = 0
        self.third_attack_delay = 0
        self.third_shoot_time = 0

        if enemy_type == "default":
            self.color = (60, 60, 60)
            self.size = 35
        elif enemy_type == "homing":
            self.color = (207, 179, 91)
            self.size = 30
        elif enemy_type == "chaser":
            self.color = (255, 80, 91)
            self.size = 28
        elif enemy_type == "shooter":
            self.color = (120,120,255)
            self.size = 25
        elif enemy_type == "sniper":
            self.color = (190,170,255)
            self.size = 25
            self.shoot_cooldown = 3.0
        elif enemy_type == "explosive_sniper":
            self.color = (255,30,30)
            self.size = 22
            self.shoot_cooldown = 2.2
        elif enemy_type == "gunner":
            self.color = (200,200,30)
            self.size = 25
            self.shoot_cooldown = 0.3
        elif enemy_type == "marauder":
            self.color = (255,255,255)
            self.size = 26
            self.shoot_cooldown = 0.2
            self.second_attack_delay = 3.0
            self.third_attack_delay = 0.4
        else:
            self.color = color
            self.size = 60

        self.rect = pygame.Rect(x - self.size, y - self.size, self.size*2, self.size*2)

    def take_damage(self, amount):
        Sounds[3].play()
        self.health -= amount
        if self.health <= 0:
            self.die()
        else:
            self.healthbar.update(self.health)

    def die(self):
        self.alive=False

    def movement(self, delta_time, walls, players=None):
        if (self.enemy_type == "homing" or self.enemy_type == "chaser" or self.enemy_type == "marauder") and players:
            self._homing_move(delta_time, walls, players)
        else:
            self._default_move(delta_time, walls)

        self.rect.topleft = (self.x - self.size, self.y - self.size)

    def _default_move(self, delta_time, walls):
        # przelicz kąt na radiany
        rad = math.radians(self.direction)

        # wylicz wektor kierunku
        dx = math.cos(rad)
        dy = math.sin(rad)

        # oblicz przesunięcie floatowe
        move_x = round(dx * self.speed * delta_time * 4)
        move_y = round(dy * self.speed * delta_time * 4)

        # porusz się krok po kroku (po jednym pikselu), aby wykryć kolizję
        step_x = int(math.copysign(1, move_x)) if move_x != 0 else 0
        for _ in range(abs(int(move_x))):
            if not self.check_collision(self.x + step_x, self.y, walls):
                self.x += step_x
            else:
                # odbicie — odwróć kierunek na osi X
                self.direction = (180 - self.direction) % 360
                break

        step_y = int(math.copysign(1, move_y)) if move_y != 0 else 0
        for _ in range(abs(int(move_y))):
            if not self.check_collision(self.x, self.y + step_y, walls):
                self.y += step_y
            else:
                # odbicie — odwróć kierunek na osi Y
                self.direction = (-self.direction) % 360
                break

    def _homing_move(self, delta_time, walls, players):
        # Znajdź najbliższego gracza w zasięgu 400 px
        seeker_distance=400
        if self.enemy_type == "chaser":
            seeker_distance=800
        if self.enemy_type == "marauder":
            seeker_distance=4000
        target = self._find_nearest_player(players, max_distance=seeker_distance)
        if target:
            dx = target.x - self.x
            dy = target.y - self.y
            target_angle = math.degrees(math.atan2(dy, dx))

            # Stopniowo skręć w kierunku celu
            angle_diff = (target_angle - self.direction + 360) % 360
            if angle_diff > 180:
                angle_diff -= 360

            max_turn = 3  # stopnie na klatkę, można dostosować prędkość skrętu
            if self.enemy_type == "chaser":
                max_turn = 6
            if self.enemy_type == "marauder":
                max_turn = 0.25
            if angle_diff > max_turn:
                self.direction += max_turn
            elif angle_diff < -max_turn:
                self.direction -= max_turn
            else:
                self.direction = target_angle

            self.direction %= 360

        # Po obróceniu wykonaj ruch jak w default_move
        self._default_move(delta_time, walls)

    def _find_nearest_player(self, players, max_distance=400):
        nearest_target = None
        nearest_dist = max_distance

        for player in players.values():
            if player.alive:
                dist = math.hypot(player.x - self.x, player.y - self.y)
                if dist < nearest_dist:
                    nearest_dist = dist
                    nearest_target = player

        return nearest_target

    def check_collision(self, new_x, new_y, walls):
        radius = int(self.size * 0.8)
        hitbox = pygame.Rect(new_x - radius, new_y - radius, radius * 2, radius * 2)
        for wall in walls:
            if hitbox.colliderect(wall.get_rect()):
                return True
        return False

    def draw(self, surface, cam_x, cam_y):
        pos = (int(self.x - cam_x), int(self.y - cam_y))
        glow_surface = pygame.Surface((self.size * 8, self.size * 8), pygame.SRCALPHA)
        glow_rect = glow_surface.get_rect(center=pos)
        for i in range(4, 0, -1):
            alpha = 80 // i  # słabsza im dalej
            radius = self.size+i*5
            pygame.draw.circle(glow_surface, (*self.color, alpha), (glow_rect.width // 2, glow_rect.height // 2), radius)
        surface.blit(glow_surface, glow_rect.topleft)
        pygame.draw.circle(surface, self.color, (int(self.x - cam_x), int(self.y - cam_y)), self.size)
        if self.enemy_type != "display":
            self.healthbar.draw(surface, cam_x, cam_y)

    def try_shoot_nearest_player(self, players, bullets):
        if (self.enemy_type != "shooter" and self.enemy_type != "sniper" and self.enemy_type != "explosive_sniper" and self.enemy_type != "gunner" and self.enemy_type != "marauder"):
            return
        from bullet import Bullet
        current_time = time.time()
        if self.enemy_type == "marauder":
            if current_time - self.third_shoot_time >= self.third_attack_delay:
                angle=random.uniform(0,359)
                bullet0=Bullet(owner_id=self.enemy_id,x=self.x,y=self.y,direction=angle,speed=self.speed+5,bullet_type=["ricochet"],damage=0,radius=10,color=self.color,team="Enemies")
                bullets.append(bullet0)
                Sounds[4].play()
                self.third_shoot_time = current_time

        if current_time - self.last_shot_time < self.shoot_cooldown:
            return
        seeker_radius=1000
        spread=0.1
        if (self.enemy_type == "sniper" or self.enemy_type == "explosive_sniper"):
            seeker_radius=1200
            spread=0
        if self.enemy_type == "gunner":
            seeker_radius=600
            spread=0.15
        if self.enemy_type == "marauder":
            seeker_radius=400
            spread=0.2
        # znajdź najbliższego gracza
        nearest_player = None
        nearest_distance = float('inf')
        for player in players.values():
            if player.alive:
                dx = player.x - self.x
                dy = player.y - self.y
                distance = (dx**2 + dy**2) ** 0.5
                if distance < nearest_distance and distance <= seeker_radius:
                    nearest_distance = distance
                    nearest_player = player

        if nearest_player:
            # oblicz kąt do gracza
            dx = nearest_player.x - self.x
            dy = nearest_player.y - self.y
            angle = math.degrees(math.atan2(dy, dx)+random.uniform(-spread,spread))
            bspeed=20 + self.speed
            bradius=10
            boffset=0
            bhs=0
            bcolor=self.color
            btype=["default"]
            if self.enemy_type == "shooter":
                Sounds[0].play()
            if self.enemy_type == "gunner":
                bspeed=10 + self.speed
                bradius=15
                Sounds[0].play()
            if (self.enemy_type == "sniper" or self.enemy_type == "explosive_sniper"):
                bspeed= 80 + self.speed
                bradius=12
                Sounds[0].play()
            if self.enemy_type == "explosive_sniper":
                Sounds[1].play()
                btype=["explosive"]
            if self.enemy_type == "marauder":
                bspeed=25 + self.speed
                bradius=9
                boffset=25
                bhs=1
                bcolor=(30,30,255)
                btype=["homing"]
                Sounds[0].play()
            bullet = Bullet(owner_id=self.enemy_id,x=self.x+boffset,y=self.y,direction=angle,speed=bspeed+20,bullet_type=btype,damage=0,radius=bradius,color=bcolor,team="Enemies",homing_strength=bhs)
            if self.enemy_type == "marauder":
                angle = math.degrees(math.atan2(dy, dx)+random.uniform(-spread,spread))
                bullet2=Bullet(owner_id=self.enemy_id,x=self.x-boffset,y=self.y,direction=angle,speed=bspeed+20,bullet_type=btype,damage=0,radius=bradius,color=(30,30,255),team="Enemies",homing_strength=bhs)
                bullets.append(bullet2)
                Sounds[0].play()
                if current_time - self.second_shoot_time >= self.second_attack_delay:
                    self.second_shoot_time = current_time
                    angle = math.degrees(math.atan2(dy, dx))
                    bullet3=Bullet(owner_id=self.enemy_id,x=self.x,y=self.y-boffset//2,direction=angle,speed=bspeed+75,bullet_type=["explosive"],damage=0,radius=12,color=(255,90,90),team="Enemies")
                    bullets.append(bullet3)
                    Sounds[1].play()
            bullets.append(bullet)
            self.last_shot_time = current_time