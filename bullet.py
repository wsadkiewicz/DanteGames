import pygame
import math
import itertools

class Bullet:
    _id_counter = itertools.count(1)

    def __init__(self, owner_id, x, y, direction, speed=10, bullet_type=None, damage=10, radius=7, color = (0,255,0)):
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

    def move(self, delta_time):
        rad = math.radians(self.direction)
        dx = math.cos(rad) * self.speed * delta_time * 100
        dy = math.sin(rad) * self.speed * delta_time * 100
        self.x += dx
        self.y += dy

    def check_collision(self, walls, players, enemies):
        if not self.alive:
            return

        hitbox = pygame.Rect(int(self.x - self.radius), int(self.y - self.radius), self.radius * 2, self.radius * 2)

        # Kolizja ze ścianą
        for wall in walls:
            if hitbox.colliderect(wall.get_rect()):
                self.alive = False
                return

        # Kolizja z graczami
        for player in players.values():
            if player.player_id != self.owner:
                if self._collides_with_circle(player.x, player.y, player.size):
                    self.alive = False
                    return

        # Kolizja z przeciwnikami
        for enemy in enemies:
            if enemy.enemy_id != self.owner:
                if self._collides_with_circle(enemy.x, enemy.y, enemy.size):
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