import pygame
import math
from game_config import SCREEN_WIDTH, SCREEN_HEIGHT

class Player:
    def __init__(self, keymap=None, color=(255, 0, 0)):
        self.x = 0
        self.y = 0
        self.speed = 5
        self.size = 25
        self.camera_x = 0
        self.camera_y = 0

        self.color = color
        self.keymap = keymap or {
            "up": None,
            "down": None,
            "left": None,
            "right": None,
            "slow": None
        }

    def movement(self, delta_time, walls):
        keys = pygame.key.get_pressed()
        current_speed = self.speed

        if (
            keys[pygame.K_LSHIFT]
            or keys[pygame.K_RSHIFT]
            or (self.keymap["slow"] and keys[self.keymap["slow"]])
        ):
            current_speed *= 0.5

        move_x = 0
        move_y = 0

        if keys[pygame.K_UP] or (self.keymap["up"] and keys[self.keymap["up"]]):
            move_y -= 1
        if keys[pygame.K_DOWN] or (self.keymap["down"] and keys[self.keymap["down"]]):
            move_y += 1
        if keys[pygame.K_LEFT] or (self.keymap["left"] and keys[self.keymap["left"]]):
            move_x -= 1
        if keys[pygame.K_RIGHT] or (self.keymap["right"] and keys[self.keymap["right"]]):
            move_x += 1

        if move_x != 0 or move_y != 0:
            length = math.sqrt(move_x ** 2 + move_y ** 2)
            move_x /= length
            move_y /= length

        dx = round(move_x * current_speed * delta_time * 100)
        dy = round(move_y * current_speed * delta_time * 100)

        step_x = int(math.copysign(1, dx)) if dx != 0 else 0
        for _ in range(abs(dx)):
            if not self.check_collision(self.x + step_x, self.y, walls):
                self.x += step_x
            else:
                break

        step_y = int(math.copysign(1, dy)) if dy != 0 else 0
        for _ in range(abs(dy)):
            if not self.check_collision(self.x, self.y + step_y, walls):
                self.y += step_y
            else:
                break

        self.camera_x = self.x - SCREEN_WIDTH // 2
        self.camera_y = self.y - SCREEN_HEIGHT // 2

    def check_collision(self, new_x, new_y, walls):
        radius = int(self.size * 0.9)
        hitbox = pygame.Rect(new_x - radius, new_y - radius, radius * 2, radius * 2)
        for wall in walls:
            if hitbox.colliderect(wall.get_rect()):
                return True
        return False

    def draw(self, surface, camera_x, camera_y):
        screen_x = int(self.x - camera_x)
        screen_y = int(self.y - camera_y)
        pygame.draw.circle(surface, self.color, (screen_x, screen_y), self.size)