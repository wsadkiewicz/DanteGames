import socket
import json
import pygame
import sys

SERVER_IP = '127.0.0.1'  # zmień na IP serwera w sieci
PORT = 25576

def recv_msg(sock):
    try:
        raw_len = sock.recv(4)
        if not raw_len:
            return None
        msg_len = int.from_bytes(raw_len, "big")

        data = b''
        while len(data) < msg_len:
            packet = sock.recv(msg_len - len(data))
            if not packet:
                return None
            data += packet
        return json.loads(data.decode())
    except Exception as e:
        print(f"Błąd odbioru danych: {e}")
        return None

pygame.init()
screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER_IP, PORT))

running = True
while running:
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

    # Wyślij dane do serwera
    try:
        msg = json.dumps({"dx": dx, "dy": dy}).encode()
        client_socket.sendall(msg)
    except:
        print("Utracono połączenie z serwerem.")
        break

    # Odbierz stan gry
    data = recv_msg(client_socket)
    if data:
        screen.fill((30, 30, 30))
        for wall in data["walls"]:
            pygame.draw.rect(screen, (0, 100, 255), pygame.Rect(wall["x"], wall["y"], wall["w"], wall["h"]))
        for player in data["players"]:
            pygame.draw.circle(screen, (255, 0, 0), (int(player["x"]), int(player["y"])), 20)
        pygame.display.flip()

pygame.quit()
client_socket.close()
sys.exit()