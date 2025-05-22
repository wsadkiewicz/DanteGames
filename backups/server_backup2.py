import socket
import select
import json
from network import recv_json, send_json  # używamy dokładnie tych samych funkcji co klient

HOST = '0.0.0.0'
PORT = 25576

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen()
server_socket.setblocking(False)

inputs = [server_socket]
clients = {}
player_states = {}  # dane o pozycjach graczy
walls = [{"x": 200, "y": 200, "w": 300, "h": 50}]  # stałe ściany

print(f"Serwer uruchomiony na {HOST}:{PORT}")

try:
    while True:
        readable, _, exceptional = select.select(inputs, [], inputs, 0.05)

        for s in readable:
            if s is server_socket:
                client_socket, addr = server_socket.accept()
                print(f"Nowe połączenie od {addr}")
                client_socket.setblocking(False)
                inputs.append(client_socket)
                clients[client_socket] = addr
                player_states[client_socket] = {"x": 100, "y": 100}
            else:
                try:
                    command = recv_json(s)
                    if command is None:
                        raise ConnectionResetError

                    dx = command.get("dx", 0)
                    dy = command.get("dy", 0)
                    if s in player_states:
                        player_states[s]["x"] += dx
                        player_states[s]["y"] += dy

                except (ConnectionResetError, ConnectionAbortedError, json.JSONDecodeError):
                    print(f"Klient {clients.get(s)} rozłączył się")
                    if s in inputs:
                        inputs.remove(s)
                    player_states.pop(s, None)
                    clients.pop(s, None)
                    s.close()

        # Wysyłanie stanu gry do każdego klienta
        players_data = [
            {"x": state["x"], "y": state["y"]}
            for state in player_states.values()
        ]
        update_payload = {"players": players_data, "walls": walls}

        for client in list(clients):
            try:
                send_json(client, update_payload)
            except Exception as e:
                print(f"Nie udało się wysłać danych do {clients[client]}: {e}")
                if client in inputs:
                    inputs.remove(client)
                player_states.pop(client, None)
                clients.pop(client, None)
                client.close()

except KeyboardInterrupt:
    print("Zamykam serwer...")
finally:
    for sock in inputs:
        sock.close()
    server_socket.close()