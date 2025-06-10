import pygame
import math

class Enemy:
    def __init__(self, enemy_id, enemy_type="default", x=0, y=0, speed=3, direction=0):
        self.enemy_id = enemy_id
        self.enemy_type = enemy_type
        self.x = x
        self.y = y
        self.speed = speed
        self.direction = direction  # kąt w stopniach (0-359)
        self.size = 25

        if enemy_type == "default":
            self.color = (255, 0, 0)
        else:
            self.color = (255, 255, 255)

    def movement(self, delta_time, walls):
        # przelicz kąt na radiany
        rad = math.radians(self.direction)

        # wylicz wektor kierunku
        dx = math.cos(rad)
        dy = math.sin(rad)

        # oblicz przesunięcie floatowe
        move_x = round(dx * self.speed * delta_time * 100)
        move_y = round(dy * self.speed * delta_time * 100)

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

    def check_collision(self, new_x, new_y, walls):
        radius = int(self.size * 0.8)
        hitbox = pygame.Rect(new_x - radius, new_y - radius, radius * 2, radius * 2)
        for wall in walls:
            if hitbox.colliderect(wall.get_rect()):
                return True
        return False

    def draw(self, surface, cam_x, cam_y):
        pygame.draw.circle(surface, self.color, (int(self.x - cam_x), int(self.y - cam_y)), self.size)