import pygame
from enemy import Enemy
from game_config import Sounds

class Explosion:
    def __init__(self, x, y, radius=400, max_lifetime=0.5, damage=30, owner=None):
        self.x = x
        self.y = y
        self.radius = radius
        self.max_lifetime = max_lifetime
        self.damage = damage
        self.elapsed_time = 0
        self.alive = True
        self.alpha = 255
        self.owner = owner

    def update(self, delta_time):
        self.elapsed_time += delta_time
        if self.elapsed_time >= self.max_lifetime:
            self.alive = False
            self.alpha = 0
        else:
            self.alpha = int(255 * (1 - self.elapsed_time / self.max_lifetime))

    def draw(self, surface, cam_x, cam_y):
        if self.alive:
            s = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
            color = (255, 100, 0, self.alpha)
            pygame.draw.circle(s, color, (self.radius, self.radius), self.radius)
            surface.blit(s, (self.x - self.radius - cam_x, self.y - self.radius - cam_y))

    def damage_enemies(self, enemies=None, players=None):
        # Zadaj obrażenia raz na start eksplozji
        if self.elapsed_time == 0:
            Sounds[2].play()
            for enemy in enemies:
                dx = enemy.x - self.x
                dy = enemy.y - self.y
                distance = (dx**2 + dy**2)**0.5
                distance2 = self.radius + enemy.size
                if distance <= distance2:
                    enemy.take_damage(self.damage)
            from player import Player
            for player in players.values():
                if player.player_id != self.owner:
                    dx = player.x - self.x
                    dy = player.y - self.y
                    distance = (dx**2 + dy**2)**0.5
                    if distance <= self.radius + player.size:
                        player.take_damage()