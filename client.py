import asyncio
import json
import pygame
import sys

SERVER_IP = '127.0.0.1'
PORT = 25576

class UDPClientProtocol:
    def __init__(self):
        self.transport = None
        self.game_state = None

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data, addr):
        try:
            self.game_state = json.loads(data.decode())
        except Exception as e:
            print("Błąd dekodowania danych:", e)

    def send_input(self, dx, dy):
        message = json.dumps({"dx": dx, "dy": dy}).encode()
        self.transport.sendto(message, (SERVER_IP, PORT))

async def main():
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    clock = pygame.time.Clock()

    loop = asyncio.get_running_loop()
    transport, protocol = await loop.create_datagram_endpoint(
        lambda: UDPClientProtocol(),
        remote_addr=(SERVER_IP, PORT)
    )

    running = True
    while running:
        await asyncio.sleep(0)  # allow asyncio to switch tasks
        dt = clock.tick(60) / 1000
        dx, dy = 0, 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]: dy -= 5
        if keys[pygame.K_s]: dy += 5
        if keys[pygame.K_a]: dx -= 5
        if keys[pygame.K_d]: dx += 5

        protocol.send_input(dx, dy)

        if protocol.game_state:
            screen.fill((30, 30, 30))
            for wall in protocol.game_state["walls"]:
                pygame.draw.rect(screen, (0, 100, 255), pygame.Rect(wall["x"], wall["y"], wall["w"], wall["h"]))
            for player in protocol.game_state["players"]:
                pygame.draw.circle(screen, (255, 0, 0), (int(player["x"]), int(player["y"])), 20)
            pygame.display.flip()

    pygame.quit()
    transport.close()
    sys.exit()

if __name__ == "__main__":
    asyncio.run(main())