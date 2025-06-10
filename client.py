import asyncio
import pygame
import sys
import random
from client_config import screen, clock, SCREEN_WIDTH, SCREEN_HEIGHT, font
from network import NetworkPacket
from level import Level
from player import Player
from game_object import GameObject

SERVER_IP = '127.0.0.1'
PORT = 25546

player_id = None
player_color = [random.randint(50, 255) for _ in range(3)]

class UDPClientProtocol:
    def __init__(self):
        self.transport = None
        self.level = Level()
        self.id_received = False

    def connection_made(self, transport):
        self.transport = transport
        # Wysyłamy pakiet inicjalizacyjny z kolorem
        packet = NetworkPacket(
            packet_type="init",
            player_id=None,
            input_data=None,
            player_color=player_color
        )
        self.send_packet(packet)

    def datagram_received(self, data, addr):
        global player_id
        try:
            packet = NetworkPacket.from_bytes(data)
            # print(f"Odebrano pakiet typu: {packet.packet_type}")

            if packet.packet_type == "init" and not self.id_received:
                player_id = packet.player_id
                self.id_received = True
                print(f"Przypisano player_id: {player_id}")
            elif packet.packet_type == "state":
                self.update_level_from_state(packet.state_data)
        except Exception as e:
            print("Błąd odbioru:", e)

    def send_packet(self, packet: NetworkPacket):
        data = packet.to_bytes()
        self.transport.sendto(data, (SERVER_IP, PORT))

    def send_input(self, input_dict):
        if player_id is None:
            return
        packet = NetworkPacket(
            packet_type="input",
            player_id=player_id,
            input_data=input_dict
        )
        # print(f"Wysyłam input do serwera: {input_dict}")
        self.send_packet(packet)

    def send_disconnect(self):
        if player_id is None:
            return
        packet = NetworkPacket(
            packet_type="disconnect",
            player_id=player_id
        )
        self.send_packet(packet)

    def update_level_from_state(self, state_data):
        self.level.players.clear()
        self.level.walls.clear()
        self.level.enemies.clear()

        # Dodaj ściany
        for w in state_data.get("walls", []):
            wall = GameObject(w["x"], w["y"], w["w"], w["h"])
            self.level.add_wall(wall)

        # Dodaj graczy
        for p in state_data.get("players", []):
            player = Player(color=tuple(p.get("color", (255, 0, 0))), player_id=p["id"])
            player.x = p["x"]
            player.y = p["y"]
            self.level.add_player(player.player_id, player)

        # Dodaj przeciwników
        for e in state_data.get("enemies", []):
            from enemy import Enemy
            enemy = Enemy(enemy_id=e["id"], x=e["x"], y=e["y"])
            enemy.color = tuple(e.get("color", (255, 0, 0)))
            self.level.add_enemy(enemy)

async def main():
    pygame.init()
    loop = asyncio.get_running_loop()

    transport, protocol = await loop.create_datagram_endpoint(
        lambda: UDPClientProtocol(),
        remote_addr=(SERVER_IP, PORT)
    )

    running = True
    while running:
        await asyncio.sleep(0)
        dt = clock.tick(60) / 1000

        dx, dy = 0, 0
        slow = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    print("Wybrano ESC – rozłączanie")
                    protocol.send_disconnect()
                    running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]: dy -= 1
        if keys[pygame.K_s]: dy += 1
        if keys[pygame.K_a]: dx -= 1
        if keys[pygame.K_d]: dx += 1
        if keys[pygame.K_LSHIFT]: slow = True

        input_data = {
            "up": dy < 0,
            "down": dy > 0,
            "left": dx < 0,
            "right": dx > 0,
            "slow": slow
        }

        if protocol.id_received:
            protocol.send_input(input_data)

        if not protocol.level.players or player_id is None:
            # Nie mamy jeszcze danych
            screen.fill((0, 0, 0))
            wait_text = font.render("Czekam na serwer...", True, (255, 255, 255))
            screen.blit(wait_text, (SCREEN_WIDTH // 2 - wait_text.get_width() // 2, SCREEN_HEIGHT // 2))
            pygame.display.flip()
            continue

        me = protocol.level.players.get(player_id)
        if not me:
            print(f"Brak danych gracza {player_id} w stanie poziomu!")
            pygame.quit()
            transport.close()
            sys.exit()

        cam_x = me.x - SCREEN_WIDTH // 2
        cam_y = me.y - SCREEN_HEIGHT // 2

        screen.fill((30, 30, 30))

        # Rysuj ściany
        for wall in protocol.level.walls:
            rect = pygame.Rect(wall.rect.x - cam_x, wall.rect.y - cam_y, wall.rect.width, wall.rect.height)
            pygame.draw.rect(screen, wall.color, rect)

        # Rysuj graczy
        for player in protocol.level.players.values():
            pygame.draw.circle(screen, player.color, (int(player.x - cam_x), int(player.y - cam_y)), player.size)

        # Rysuj przeciwników
        for enemy in protocol.level.enemies:
            enemy.draw(screen, cam_x, cam_y)

        pos_text = font.render(f"x: {int(me.x)} y: {int(me.y)}", True, (255, 255, 255))
        screen.blit(pos_text, (10, 10))

        pygame.display.flip()

    pygame.quit()
    transport.close()
    sys.exit()

if __name__ == "__main__":
    asyncio.run(main())