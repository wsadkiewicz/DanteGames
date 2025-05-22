import socket
import select
import json
from network import recv_json, send_json

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

def send_msg(sock, obj):
    try:
        msg = json.dumps(obj).encode()
        msg_len = len(msg).to_bytes(4, "big")
        sock.sendall(msg_len + msg)
    except Exception as e:
        print(f"Błąd wysyłania: {e}")

try:
    while True:
        readable, _, _ = select.select(inputs, [], [], 0.1)
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
                    if command:
                        dx = command.get("dx", 0)
                        dy = command.get("dy", 0)
                        if s in player_states:
                            player_states[s]["x"] += dx
                            player_states[s]["y"] += dy
                    else:
                        raise ConnectionResetError
                except (ConnectionResetError, ConnectionAbortedError):
                    print(f"Klient {clients[s]} rozłączył się")
                    inputs.remove(s)
                    player_states.pop(s, None)
                    clients.pop(s, None)
                    s.close()

        players_data = [player_states[c] for c in clients if c in player_states]
        update_payload = {"players": players_data, "walls": walls}
        for client in clients:
            try:
                send_json(client, update_payload)
            except:
                pass

except KeyboardInterrupt:
    print("Zamykam serwer...")
finally:
    server_socket.close()