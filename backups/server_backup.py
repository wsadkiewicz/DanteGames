import socket
import select

HOST = '0.0.0.0'
PORT = 25576

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server_socket.bind((HOST, PORT))
server_socket.listen()
server_socket.setblocking(False)

inputs = [server_socket]
clients = {}

print(f"Serwer uruchomiony na {HOST}:{PORT}")

try:
    while True:
        readable, _, _ = select.select(inputs, [], [], 0.1)  # timeout 0.1 sekundy

        for s in readable:
            if s is server_socket:
                client_socket, addr = server_socket.accept()
                print(f"Nowe połączenie od {addr}")
                client_socket.setblocking(False)
                inputs.append(client_socket)
                clients[client_socket] = addr
            else:
                try:
                    data = s.recv(1024)
                except ConnectionResetError:
                    data = None

                if data:
                    print(f"Otrzymano od {clients[s]}: {data.decode()}")
                    # Tu możesz dodać logikę np. wysłania odpowiedzi do klienta:
                    # s.sendall(b"Potwierdzenie")
                else:
                    print(f"Klient {clients[s]} rozłączył się")
                    inputs.remove(s)
                    s.close()
                    del clients[s]
except KeyboardInterrupt:
    print("Zamykam serwer...")
finally:
    server_socket.close()