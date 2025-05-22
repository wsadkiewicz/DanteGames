import asyncio
import json
import time

PORT = 25576
clients = {}  # {addr: {"x": ..., "y": ..., "last_seen": timestamp}}

class GameServer(asyncio.DatagramProtocol):
    def connection_made(self, transport):
        self.transport = transport
        print(f"Serwer UDP nasłuchuje na porcie {PORT}")

    def datagram_received(self, data, addr):
        try:
            message = json.loads(data.decode())
            dx = message.get("dx", 0)
            dy = message.get("dy", 0)

            player = clients.get(addr, {"x": 100, "y": 100, "last_seen": 0})
            player["x"] += dx
            player["y"] += dy
            player["last_seen"] = time.time()
            clients[addr] = player

        except Exception as e:
            print(f"Błąd odbioru od {addr}: {e}")

    def broadcast_state(self):
        # Usuń nieaktywnych klientów (brak aktywności > 5s)
        now = time.time()
        to_remove = [addr for addr, p in clients.items() if now - p["last_seen"] > 5]
        for addr in to_remove:
            print(f"Usuwam nieaktywnego klienta: {addr}")
            clients.pop(addr)

        players = [{"x": p["x"], "y": p["y"]} for p in clients.values()]
        state = {"players": players, "walls": [{"x": 200, "y": 200, "w": 300, "h": 50}]}
        data = json.dumps(state).encode()

        for addr in clients:
            self.transport.sendto(data, addr)

async def broadcast_loop(server):
    while True:
        await asyncio.sleep(0.04) #Tutaj ms opoznienia serwera
        server.broadcast_state()

async def main():
    loop = asyncio.get_running_loop()
    print("Uruchamiam serwer...")

    transport, protocol = await loop.create_datagram_endpoint(
        lambda: GameServer(),
        local_addr=("0.0.0.0", PORT)
    )

    # Start pętli broadcastu
    asyncio.create_task(broadcast_loop(protocol))

    try:
        await asyncio.Future()  # działa w nieskończoność
    finally:
        transport.close()

if __name__ == "__main__":
    asyncio.run(main())