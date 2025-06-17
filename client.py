# client.py
import pygame
import asyncio
import pickle
import socket
import traceback
import os
from game_config_singleplayer import screen, font, clock, SCREEN_WIDTH, SCREEN_HEIGHT
from player import Player  # Upewnij się, że plik player.py zawiera klasę Player
from game_config import Sounds

SERVER_IP = '127.0.0.1'
SERVER_PORT = 25345


def draw_grid(surface, cam_x, cam_y, grid_size=50):
    grid_color = (50, 0, 70)  # ciemny fioletowy

    width, height = surface.get_size()

    # przesunięcie siatki o kamerę (kam_x, cam_y)
    offset_x = cam_x % grid_size
    offset_y = cam_y % grid_size

    # pionowe linie
    for x in range(-offset_x, width, grid_size):
        pygame.draw.line(surface, grid_color, (x, 0), (x, height))

    # poziome linie
    for y in range(-offset_y, height, grid_size):
        pygame.draw.line(surface, grid_color, (0, y), (width, y))


class GameClient:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setblocking(False)
        self.server_address = (SERVER_IP, SERVER_PORT)
        self.level = None
        self.player_id = None
        self.player = None
        self.connected = False

    def send_disconnect(self):
        disconnect_msg = {"disconnect": True}
        self.sock.sendto(pickle.dumps(disconnect_msg), self.server_address)

    def load_player_stats(self):
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        stats_path = os.path.join(BASE_DIR, "player_stats.txt")

        with open(stats_path, "r") as f:
            lines = f.read().splitlines()
            speed = int(lines[0])
            size = int(lines[1])
            color = eval(lines[2])
            bullet_speed = int(lines[3])
            power = int(lines[4])
            bullet_type_line = lines[5].strip()
            bullet_type = bullet_type_line.split()
            return Player(size=size, speed=speed, color=color, power=power, bullet_speed=bullet_speed,bullet_type=bullet_type)

    def send_initial_player(self):
        data = {"player": self.player}
        self.sock.sendto(pickle.dumps(data), self.server_address)
        self.connected = True

    def get_input(self):
        keys = pygame.key.get_pressed()
        return {
            "up": keys[pygame.K_w],
            "down": keys[pygame.K_s],
            "left": keys[pygame.K_a],
            "right": keys[pygame.K_d],
            "slow": keys[pygame.K_LSHIFT],
            "mouse_left": pygame.mouse.get_pressed()[0],
            "mouse_pos": pygame.mouse.get_pos(),
        }

    async def send_input(self):
        if self.connected:
            input_data = {"keys": self.get_input()}
            self.sock.sendto(pickle.dumps(input_data), self.server_address)

    async def receive_game_state(self):
        try:
            data, _ = self.sock.recvfrom(65536)
            packet = pickle.loads(data)
            self.level = packet.get("level", None)
            self.player_id = packet.get("player_id", None)
            if self.player_id and self.player:
                self.player.player_id = self.player_id
        except BlockingIOError:
            pass
        except Exception as e:
            print(f"Błąd odbierania stanu gry: {e}")
            traceback.print_exc()

    async def run(self):
        pygame.init()
        try:
            self.player = self.load_player_stats()
            self.send_initial_player()

            while True:
                dt = clock.tick(60) / 1000
                await self.send_input()
                await self.receive_game_state()

                screen.fill((0, 0, 0))

                if self.level and self.player_id:
                    player = self.level.players.get(self.player_id)
                    cam_x = player.x - SCREEN_WIDTH // 2 if player else 0
                    cam_y = player.y - SCREEN_HEIGHT // 2 if player else 0
                    draw_grid(screen, cam_x, cam_y, grid_size=50)

                    if self.level.images:
                        self.level.draw_images(screen)
                    for wall in self.level.walls:
                        wall.draw(screen, cam_x, cam_y, draw_glow_only=True)
                    for wall in self.level.walls:
                        wall.draw(screen, cam_x, cam_y, draw_glow_only=False)
                    for enemy in self.level.enemies:
                        enemy.draw(screen, cam_x, cam_y)
                    for bullet in self.level.bullets:
                        bullet.draw(screen, cam_x, cam_y)
                    for button in self.level.buttons:
                        button.draw(screen)
                    for text in self.level.texts:
                        text.draw(screen)
                    for p in self.level.players.values():
                        p.draw(screen, cam_x, cam_y)
                    for explosion in self.level.explosions:
                        explosion.draw(screen, cam_x, cam_y)

                pygame.display.flip()

                for event in pygame.event.get():
                    if event.type == pygame.QUIT or (
                        event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                        self.send_disconnect()
                        return

                await asyncio.sleep(0)

        except Exception as e:
            print("Wystąpił błąd podczas działania klienta:")
            traceback.print_exc()
            input("Naciśnij Enter, aby zamknąć...")

        finally:
            pygame.quit()


if __name__ == "__main__":
    try:
        asyncio.run(GameClient().run())
    except Exception as e:
        print("Błąd krytyczny przy uruchamianiu klienta:")
        traceback.print_exc()
        input("Naciśnij Enter, aby zamknąć...")