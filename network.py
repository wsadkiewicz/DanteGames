import json
import socket

def send_json(sock, data):
    msg = json.dumps(data).encode('utf-8')
    length = len(msg).to_bytes(4, byteorder='big')
    sock.sendall(length + msg)

def recv_json(sock):
    length_bytes = sock.recv(4)
    if not length_bytes:
        return None
    length = int.from_bytes(length_bytes, byteorder='big')
    data = sock.recv(length)
    return json.loads(data.decode('utf-8'))