import pygame
import sys
import math

# Inicjalizacja Pygame
pygame.init()

# Ustawienia ekranu
info = pygame.display.Info()
SCREEN_WIDTH, SCREEN_HEIGHT = info.current_w, info.current_h
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Dante Games")

# Czcionka
font = pygame.font.SysFont(None, 36)

# Zegar
clock = pygame.time.Clock()


class Level:
    def __init__(self):
        self.walls = []
        self.players = []

    def add_wall(self, wall):
        self.walls.append(wall)

    def add_player(self, player):
        self.players.append(player)

    def update(self, delta_time):
        for player in self.players:
            player.movement(delta_time, self.walls)

    def draw(self, surface, player_index):
        if not (0 <= player_index < len(self.players)):
            raise ValueError("Nieprawidłowy indeks gracza")

        # Gracz, którego perspektywę rysujemy
        observer = self.players[player_index]
        cam_x = observer.camera_x
        cam_y = observer.camera_y

        # Czyścimy ekran / widok
        surface.fill((30, 30, 30))

        # Rysujemy ściany z perspektywy obserwującego gracza
        for wall in self.walls:
            wall.draw(surface, cam_x, cam_y)

        # Rysujemy wszystkich graczy względem tej kamery
        for p in self.players:
            p.draw(surface, cam_x, cam_y)

        # HUD tylko dla obserwującego gracza
        pos_text = font.render(f"x: {int(observer.x)}  y: {int(observer.y)}", True, (255, 255, 255))
        surface.blit(pos_text, (10, 10))


# Klasa GameObject (np. ściana)
class GameObject:
    def __init__(self, x, y, width, height, color=(0, 100, 255)):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color

    def draw(self, surface, camera_x, camera_y):
        screen_rect = self.rect.move(-camera_x, -camera_y)
        pygame.draw.rect(surface, self.color, screen_rect)

    def get_rect(self):
        return self.rect


# Klasa gracza
class Player:
    def __init__(self, keymap=None, color=(255, 0, 0)):
        self.x = 0
        self.y = 0
        self.speed = 5
        self.size = 25
        self.camera_x = 0
        self.camera_y = 0

        self.color = color  # Kolor gracza

        # Mapa klawiszy – opcjonalna
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

# Tworzenie instancji poziomu
level = Level()

# Dodajemy gracza i ściany do poziomu
player = Player(keymap={
    "up": pygame.K_w,
    "down": pygame.K_s,
    "left": pygame.K_a,
    "right": pygame.K_d,
    "slow": pygame.K_LSHIFT
},color=(0,0,255))
player2 = Player()
level.add_player(player)
level.add_player(player2)

level.add_wall(GameObject(200, 200, 300, 50))
level.add_wall(GameObject(-400, 100, 150, 150))
level.add_wall(GameObject(600, 400, 100, 300))

# Główna pętla gry
running = True
while running:
    delta_time = clock.tick(60) / 1000  # czas w sekundach

    for event in pygame.event.get():
        if event.type == pygame.QUIT or (
            event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
        ):
            running = False

    level.update(delta_time)
    level.draw(screen,0)

    pygame.display.flip()

pygame.quit()
sys.exit()