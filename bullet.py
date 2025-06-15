import pygame
import math
import itertools
from explosion import Explosion

class Bullet:
    _id_counter = itertools.count(1)

    def __init__(self, owner_id, x, y, direction, speed=10, bullet_type=None, damage=10, radius=7, color = (0,255,0), bounces = 3,team=None):
        self.id = next(Bullet._id_counter)
        self.owner = owner_id
        self.x = x
        self.y = y
        self.direction = direction  # w stopniach
        self.speed = speed
        self.type = bullet_type or ["default"]
        self.damage = damage
        self.radius = radius
        self.alive = True
        self.color = color
        self.bounces = bounces
        self.explosion = None
        self.team=team

    def move(self, delta_time, walls=None, players=None, enemies=None):
        if "homing" in self.type:
            self._homing_move(delta_time, players, enemies)
        else:
            rad = math.radians(self.direction)
            dx = math.cos(rad) * self.speed * delta_time * 10
            dy = math.sin(rad) * self.speed * delta_time * 10
            self.x += dx
            self.y += dy

    def check_collision(self, walls, players, enemies, explosions=None):
        if not self.alive:
            return

        hitbox = pygame.Rect(int(self.x - self.radius), int(self.y - self.radius), self.radius * 2, self.radius * 2)

        # Kolizja ze ścianą
        for wall in walls:
            if hitbox.colliderect(wall.get_rect()):
                if "explosive" in self.type:
                    explosion = Explosion(self.x, self.y, radius=120, damage=self.damage, owner=self.owner)
                    explosions.append(explosion)
                    explosion.damage_enemies(enemies,players)
                    self.alive = False
                if "ricochet" in self.type and self.bounces > 0:
                    self._ricochet(wall)
                else:
                    self.alive = False
                return

        # Kolizja z graczami
        for player in players.values():
            if player.player_id != self.owner:
                if self._collides_with_circle(player.x, player.y, player.size):
                    if "explosive" in self.type:
                        player.take_damage(damage=2)
                        explosion = Explosion(self.x, self.y, radius=120, damage=self.damage, owner=self.owner)
                        explosions.append(explosion)
                        explosion.damage_enemies(enemies,players)
                    self.alive = False
                    player.take_damage(damage=1)
                    return

        # Kolizja z przeciwnikami
        if self.team != "Enemies":
            for enemy in enemies:
                if enemy.enemy_id != self.owner:
                    if self._collides_with_circle(enemy.x, enemy.y, enemy.size):
                        if "explosive" in self.type:
                            explosion = Explosion(self.x, self.y, radius=120, damage=self.damage, owner=self.owner)
                            explosions.append(explosion)
                            explosion.damage_enemies(enemies,players)
                        self.alive = False
                        enemy.take_damage(amount=self.damage)
                        return

    def _collides_with_circle(self, obj_x, obj_y, obj_radius):
        dx = self.x - obj_x
        dy = self.y - obj_y
        distance = math.hypot(dx, dy)
        return distance < self.radius + obj_radius

    def draw(self, surface, cam_x, cam_y):
        if self.alive:
            pygame.draw.circle(surface, self.color, (int(self.x - cam_x), int(self.y - cam_y)), self.radius)


    def _ricochet(self, wall):
        wall_rect = wall.get_rect()
        bullet_rect = pygame.Rect(int(self.x - self.radius), int(self.y - self.radius), self.radius * 2, self.radius * 2)

        rad = math.radians(self.direction)
        prev_x = self.x - math.cos(rad) * self.speed * 0.1 * 10
        prev_y = self.y - math.sin(rad) * self.speed * 0.1 * 10

        collided_x = False
        collided_y = False
  
        if not wall_rect.collidepoint(prev_x, self.y) and wall_rect.collidepoint(self.x, self.y):
            collided_x = True

        if not wall_rect.collidepoint(self.x, prev_y) and wall_rect.collidepoint(self.x, self.y):
            collided_y = True

        if collided_x:
            self.direction = (180 - self.direction) % 360
            self.bounces -= 1
        if collided_y:
            self.direction = (-self.direction) % 360
            self.bounces -= 1

    def _homing_move(self, delta_time, players, enemies):
        # Szukamy celu w zasięgu 200 px spośród graczy i przeciwników, ale nie ownera i nie ścian
        target = self._find_nearest_target(players, enemies, max_distance=500)
        if target:
            # Obliczamy kąt do celu
            dx = target.x - self.x
            dy = target.y - self.y
            target_angle = math.degrees(math.atan2(dy, dx))

            # Skręcamy w kierunku celu, np. maksymalnie 5 stopni na ruch
            angle_diff = (target_angle - self.direction + 360) % 360
            if angle_diff > 180:
                angle_diff -= 360

            max_turn = 3  # stopni na klatkę
            if angle_diff > max_turn:
                self.direction += max_turn
            elif angle_diff < -max_turn:
                self.direction -= max_turn
            else:
                self.direction = target_angle

            self.direction %= 360

        # Następnie poruszamy się w nowym kierunku
        rad = math.radians(self.direction)
        dx = math.cos(rad) * self.speed * delta_time * 10
        dy = math.sin(rad) * self.speed * delta_time * 10
        self.x += dx
        self.y += dy

    def _find_nearest_target(self, players, enemies, max_distance=200):
        nearest_target = None
        nearest_dist = max_distance

        # Sprawdź graczy (innych niż owner)
        if players:
            for player in players.values():
                if player.player_id == self.owner:
                    continue
                dist = math.hypot(player.x - self.x, player.y - self.y)
                if dist < nearest_dist:
                    nearest_dist = dist
                    nearest_target = player

        # Sprawdź przeciwników (innych niż owner)
        if enemies and self.team != "Enemies":
            for enemy in enemies:
                if enemy.enemy_id == self.owner:
                    continue
                dist = math.hypot(enemy.x - self.x, enemy.y - self.y)
                if dist < nearest_dist:
                    nearest_dist = dist
                    nearest_target = enemy

        return nearest_target