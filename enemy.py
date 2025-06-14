import pygame
import math
from healthbar import Healthbar
import time
import random

class Enemy:
    def __init__(self, enemy_id, enemy_type="default", x=0, y=0, speed=3, direction=0,max_health=100,shoot_cooldown=1.0):
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
        self.rect = pygame.Rect(x - self.size, y - self.size, self.size*2, self.size*2)
        self.alive=True
        self.last_shot_time = 0
        self.shoot_cooldown = shoot_cooldown
        self.second_attack_delay = 0
        self.second_shoot_time = 0

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
        else:
            self.color = (255, 255, 255)

    def take_damage(self, amount):
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
        move_x = round(dx * self.speed * delta_time * 5)
        move_y = round(dy * self.speed * delta_time * 5)

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
        if (self.enemy_type == "chaser" or self.enemy_type == "marauder"):
            seeker_distance=800
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
        pygame.draw.circle(surface, self.color, (int(self.x - cam_x), int(self.y - cam_y)), self.size)
        self.healthbar.draw(surface, cam_x, cam_y)

    def try_shoot_nearest_player(self, players, bullets):
        if (self.enemy_type != "shooter" and self.enemy_type != "sniper" and self.enemy_type != "explosive_sniper" and self.enemy_type != "gunner" and self.enemy_type != "marauder"):
            return

        current_time = time.time()
        if current_time - self.last_shot_time < self.shoot_cooldown:
            return
        seeker_radius=1000
        spread=0.1
        if (self.enemy_type == "sniper" or self.enemy_type == "explosive_sniper"):
            seeker_radius=1600
            spread=0
        if self.enemy_type == "gunner":
            seeker_radius=600
            spread=0.15
        if self.enemy_type == "marauder":
            seeker_radius=800
            spread=0.2
        # znajdź najbliższego gracza
        nearest_player = None
        nearest_distance = float('inf')
        for player in players.values():
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
            from bullet import Bullet  # uniknięcie cyklicznego importu
            bspeed=70
            bradius=10
            boffset=0
            btype=["default"]
            if self.enemy_type == "gunner":
                bspeed=55
                bradius=15
            if (self.enemy_type == "sniper" or self.enemy_type == "explosive_sniper"):
                bspeed=120
                bradius=12
            if self.enemy_type == "explosive_sniper":
                btype=["explosive"]
            if self.enemy_type == "marauder":
                bspeed=50
                bradius=9
                boffset=25
                btype=["ricochet"]
            bullet = Bullet(
                owner_id=self.enemy_id,
                x=self.x+boffset,
                y=self.y,
                direction=angle,
                speed=bspeed,
                bullet_type=btype,
                damage=0,
                radius=bradius,
                color=self.color,
                team="Enemies"
            )
            if self.enemy_type == "marauder":
                angle = math.degrees(math.atan2(dy, dx)+random.uniform(-spread,spread))
                bullet2=Bullet(owner_id=self.enemy_id,x=self.x-boffset,y=self.y,direction=angle,speed=bspeed,bullet_type=btype,damage=0,radius=bradius,color=self.color,team="Enemies")
                bullets.append(bullet2)
                if current_time - self.second_shoot_time >= self.second_attack_delay:
                    self.second_shoot_time = current_time
                    angle = math.degrees(math.atan2(dy, dx))
                    bullet3=Bullet(owner_id=self.enemy_id,x=self.x,y=self.y-boffset//2,direction=angle,speed=bspeed,bullet_type=["homing","explosive"],damage=0,radius=bradius+3,color=(90,90,90),team="Enemies")
                    bullets.append(bullet3)
            bullets.append(bullet)
            self.last_shot_time = current_time