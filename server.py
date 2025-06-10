import asyncio
import time
import pickle
from player import Player
from level import Level
from game_object import GameObject
from enemy import Enemy
from network import NetworkPacket
from enemy import Enemy
import random

PORT = 25546
clients = {}  # addr -> {"player": Player, "last_seen": time, "id": int}
clients_lock = asyncio.Lock()

level = Level()
level.add_wall(GameObject(-900, -1000, 2000, 100))                      
level.add_wall(GameObject(-1000, -1000, 100, 2000))  
level.add_wall(GameObject(-1000, 1000, 2000, 100))                    
level.add_wall(GameObject(1000, -900, 100, 2000))

for i in range(0,3,1):
    direction = random.uniform(0, 360)
    enemy = Enemy(enemy_id=10000, x=random.uniform(0,1000)-500, y=random.uniform(0,1000)-500, speed=3, direction=direction, enemy_type="default")
    level.add_enemy(enemy)

class GameServer(asyncio.DatagramProtocol):
    def __init__(self):
        self.transport = None
        self.next_id = 1

    def connection_made(self, transport):
        self.transport = transport
        print(f"Serwer nasłuchuje na porcie {PORT}")

    def datagram_received(self, data, addr):
        try:
            packet = NetworkPacket.from_bytes(data)
            asyncio.create_task(self.handle_packet(packet, addr))
        except Exception as e:
            print(f"Błąd od klienta {addr}: {e}")

    async def handle_packet(self, packet, addr):
        now = time.time()
        print(f"Odebrano pakiet od {addr} - typ: {packet.packet_type}, player_id: {getattr(packet, 'player_id', None)}")
        async with clients_lock:
            if addr not in clients:
                print(f"Nowy klient: {addr}")
                new_player = Player(color=packet.player_color or [255, 0, 0])
                new_player.player_id = self.next_id
                self.next_id += 1
                new_player.x, new_player.y = 100, 100
                level.add_player(new_player.player_id, new_player)
                clients[addr] = {
                    "player": new_player,
                    "last_seen": now,
                    "id": new_player.player_id
                }
                print(f"Dołączono gracza z {addr}, ID: {new_player.player_id}")

                init_packet = NetworkPacket(
                    packet_type="init",
                    player_id=new_player.player_id
                )
                self.transport.sendto(init_packet.to_bytes(), addr)

            if packet.packet_type == "disconnect":
                player_id_to_remove = clients[addr]["id"]
                print(f"Gracz {player_id_to_remove} z {addr} rozłączył się ręcznie")
                level.players.pop(player_id_to_remove, None)
                del clients[addr]
                return

            player = clients[addr]["player"]

        if packet.input_data:
            player.simulate_input(packet.input_data)

        async with clients_lock:
            if addr in clients:
                clients[addr]["last_seen"] = time.time()
                print(f"Zaktualizowano last_seen dla {addr}")

    async def broadcast_state(self):
        now = time.time()
        timeout = 5  # sekundy

        async with clients_lock:
            to_remove = []
            for addr, data in clients.items():
                diff = now - data["last_seen"]
                if diff > timeout:
                    print(f"Usuwam nieaktywnego gracza {addr} (ostatnia aktywność {diff:.2f}s temu)")
                    to_remove.append((addr, data["id"]))

            for addr, player_id in to_remove:
                level.players.pop(player_id, None)
                del clients[addr]

            recipients = {
                addr: clients[addr]["id"]
                for addr in clients
            }

        # Przetwarzanie stanu gry
        level.update(1 / 25)

        state = {
            "players": [
                {"id": p.player_id, "x": p.x, "y": p.y, "color": p.color}
                for p in level.players.values()
            ],
            "walls": [
                {"x": w.rect.x, "y": w.rect.y, "w": w.rect.width, "h": w.rect.height}
                for w in level.walls
            ],
            "enemies": [
                {"id": e.enemy_id,"x": e.x,"y": e.y,"color": e.color}
                for e in level.enemies
            ]
        }

        for addr, player_id in recipients.items():
            packet = NetworkPacket(
                packet_type="state",
                player_id=player_id,
                state_data=state
            )
            self.transport.sendto(packet.to_bytes(), addr)
            print(f"Wysłano stan do {addr} (id: {player_id})")

async def broadcast_loop(server):
    while True:
        await asyncio.sleep(0.04)
        await server.broadcast_state()

async def main():
    print("Uruchamianie serwera...")
    loop = asyncio.get_running_loop()
    transport, protocol = await loop.create_datagram_endpoint(
        lambda: GameServer(),
        local_addr=("0.0.0.0", PORT)
    )
    asyncio.create_task(broadcast_loop(protocol))
    try:
        await asyncio.Future()
    finally:
        transport.close()

if __name__ == "__main__":
    asyncio.run(main())