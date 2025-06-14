import pygame
import math
from bullet import Bullet
from game_config import SCREEN_WIDTH, SCREEN_HEIGHT

class Player:
    def __init__(self,keymap=None,color=(0,255,0),player_id=1,x=0,y=0,cam_x=0,cam_y=0,speed=10,size=25,lives=3,bullet_speed=12,power=5):
        self.x = x
        self.y = y
        self.speed = speed
        self.size = size
        self.camera_x = cam_x
        self.camera_y = cam_y

        self.bullet_speed = bullet_speed
        self.power=power

        self.lives=lives
        self.max_lives=lives
        self.immortal = False
        self.immortal_timer = 0

        self.color = color
        self.original_color = color
        self.player_id = player_id
        self.keymap = keymap or {
            "up": None,
            "down": None,
            "left": None,
            "right": None,
            "slow": None
        }

    def draw_lives(self, surface):
        radius = 30
        spacing = 120
        for i in range(self.max_lives):
            x = 50 + i * spacing
            y = 50
            color = (0, 200, 0) if i < self.lives else (0, 0, 0)
            pygame.draw.circle(surface, color, (x, y), radius)
            pygame.draw.circle(surface, (255, 255, 255), (x, y), radius, 1)

    def take_damage(self):
        if not self.immortal:
            self.lives -= 1
            self.immortal = True
            self.immortal_timer = 3.0

    def simulate_input(self, keys):
        self.simulated_keys = keys

    def movement(self, delta_time, walls):

        if self.immortal:
            self.immortal_timer -= delta_time
            if self.immortal_timer <= 0:
                self.immortal = False
                self.color=self.original_color
            else:
                blink_frequency = 0.2
                t = self.immortal_timer % (blink_frequency * 2)    
                def adjust_color(c, delta):
                    return max(0, min(255, c + delta))
                if t < blink_frequency:
                    self.color = tuple(adjust_color(c, -60) for c in self.original_color)
                else:
                    self.color = tuple(adjust_color(c, +40) for c in self.original_color)

        keys = getattr(self, "simulated_keys", {})
        move_x = move_y = 0
        speed = self.speed * (0.5 if keys.get("slow") else 1)

        if keys.get("up"): move_y -= 1
        if keys.get("down"): move_y += 1
        if keys.get("left"): move_x -= 1
        if keys.get("right"): move_x += 1

        if move_x != 0 or move_y != 0:
            length = math.sqrt(move_x ** 2 + move_y ** 2)
            move_x /= length
            move_y /= length

        dx = round(move_x * speed * delta_time * 100)
        dy = round(move_y * speed * delta_time * 100)

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
        radius = int(self.size * 0.8)
        hitbox = pygame.Rect(new_x - radius, new_y - radius, radius * 2, radius * 2)
        for wall in walls:
            if hitbox.colliderect(wall.get_rect()):
                return True
        return False