import pygame
import math
import os
from bullet import Bullet
from game_config import SCREEN_WIDTH, SCREEN_HEIGHT, Sounds, BASE_DIR_NAME

class Player:
    def __init__(self,keymap=None,color=(0,255,0),player_id=1,x=0,y=0,cam_x=0,cam_y=0,speed=10,size=25,lives=3,bullet_speed=12,power=5,bullet_type=["default"]):
        self.x = x
        self.y = y
        self.speed = speed
        self.size = size
        self.camera_x = cam_x
        self.camera_y = cam_y

        self.bullet_speed = bullet_speed
        self.power=power
        self.bullet_type = bullet_type

        self.lives=lives
        self.max_lives=lives
        self.immortal = True
        self.immortal_timer = 5.0
        self.shoot_delay = 0

        self.alive=True

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
        self.simulated_keys = {}

    def draw(self, screen, cam_x, cam_y):
        pos = (int(self.x - cam_x), int(self.y - cam_y))
        glow_surface = pygame.Surface((self.size * 8, self.size * 8), pygame.SRCALPHA)
        glow_rect = glow_surface.get_rect(center=pos)
        for i in range(4, 0, -1):
            alpha = 80//(i/2)
            radius = (self.size + i*2) * (self.shoot_delay+1)
            pygame.draw.circle(glow_surface, (*self.color, alpha), (glow_rect.width // 2, glow_rect.height // 2), radius)
        screen.blit(glow_surface, glow_rect.topleft)
        pygame.draw.circle(screen, self.color, (int(self.x - cam_x), int(self.y - cam_y)), self.size)

    def draw_lives(self, surface):
        heart_full = os.path.join(BASE_DIR_NAME, "assets/heart_full.png")
        heart_empty = os.path.join(BASE_DIR_NAME, "assets/heart_empty.png")
        heart_full_alpha = pygame.image.load(heart_full).convert_alpha()
        heart_empty_alpha = pygame.image.load(heart_empty).convert_alpha()
        heart_full_alpha = pygame.transform.smoothscale(heart_full_alpha, (90, 90))
        heart_empty_alpha = pygame.transform.smoothscale(heart_empty_alpha, (90, 90))
        radius = 30
        spacing = 120
        for i in range(self.max_lives):
            x = 100 + i * spacing
            y = 100
            image = heart_full_alpha if i < self.lives else heart_empty_alpha
            rect = image.get_rect(center=(x, y))
            surface.blit(image, rect.topleft)

    def take_damage(self,damage=1):
        if not self.immortal:
            Sounds[3].play()
            self.lives -= damage
            self.immortal = True
            self.immortal_timer = 3.0
        

    def simulate_input(self, keys):
        self.simulated_keys = keys
        self.mouse_pressed = keys.get("mouse_left", False)
        self.mouse_pos = keys.get("mouse_pos", (0, 0))

    def try_shoot(self, bullets, mouse_pos, mouse_click):
        if self.shoot_delay > 0 or not mouse_click:
            return
        if "explosive" in self.bullet_type:
            Sounds[1].play()
        else:
            Sounds[0].play()
        cam_x = self.x - SCREEN_WIDTH//2
        cam_y = self.y - SCREEN_HEIGHT//2
        world_mouse_x = mouse_pos[0] + cam_x 
        world_mouse_y = mouse_pos[1] + cam_y
        dx = world_mouse_x - self.x
        dy = world_mouse_y - self.y
        angle = math.degrees(math.atan2(dy, dx))

        bullet = Bullet(
            owner_id=self.player_id,
            x=self.x,
            y=self.y,
            direction=angle,
            speed=self.bullet_speed,
            radius=10,
            damage=self.power,
            color=self.original_color,
            bullet_type=self.bullet_type
        )

        bullets.append(bullet)
        self.shoot_delay = 0.4

    def movement(self, delta_time, walls, bullets, mouse_pos, mouse_click):

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

        #keys = getattr(self, "simulated_keys", {})
        keys=self.simulated_keys
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

        dx = round(move_x * speed * delta_time * 8)
        dy = round(move_y * speed * delta_time * 8)

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

        self.try_shoot(bullets,mouse_pos,mouse_click)

    def check_collision(self, new_x, new_y, walls):
        radius = int(self.size * 0.8)
        hitbox = pygame.Rect(new_x - radius, new_y - radius, radius * 2, radius * 2)
        for wall in walls:
            if hitbox.colliderect(wall.get_rect()):
                return True
        return False