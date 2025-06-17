# server.py
import asyncio
import pickle
import time
import traceback
from level import Level
from enemy import Enemy

PORT = 25345

class GameServer:
    def __init__(self):
        self.clients = {}  # addr: player_id
        self.inputs = {}   # player_id: simulated_keys
        self.level = Level()
        self.level.multiplayer = True
        self.level.load_from_file("server_level.txt")
        placeholder_enemy = Enemy(x=-5000,y=-5000,speed=0,enemy_type="default",enemy_id=-3)
        self.level.enemies.append(placeholder_enemy)
        self.last_player_id = 1

    def register_client(self, addr, player):
        if addr not in self.clients:
            player_id = self.last_player_id
            player.player_id = player_id
            self.clients[addr] = player_id
            self.level.add_player(player_id, player)
            print(f"Nowy klient: {addr} jako gracz {player_id}")
            self.last_player_id += 1
        return self.clients[addr]

    async def start(self):
        print(f"Serwer uruchomiony na porcie {PORT}")
        loop = asyncio.get_running_loop()
        transport = None

        try:
            transport, _ = await loop.create_datagram_endpoint(
                lambda: ServerProtocol(self),
                local_addr=('0.0.0.0', PORT)
            )

            last_time = time.time()

            while True:
                current_time = time.time()
                delta_time = current_time - last_time
                last_time = current_time

                self.level.update(delta_time, None, False)
                for player_id, player in self.level.players.items():
                    input_keys = self.inputs.get(player_id, {})
                    mouse_pos = input_keys.get("mouse_pos", None)
                    mouse_click = input_keys.get("mouse_left", False)
                    player.try_shoot(self.level.bullets, mouse_pos, mouse_click)

                for addr in self.clients:
                    data = {
                        "level": self.level,
                        "player_id": self.clients[addr]
                    }
                    try:
                        transport.sendto(pickle.dumps(data), addr)
                    except Exception as e:
                        print(f"Błąd wysyłania do {addr}: {e}")

                # Opcjonalne ograniczenie do 60 FPS
                await asyncio.sleep(max(0, (1 / 60) - (time.time() - current_time)))

        except Exception as e:
            print("Wystąpił błąd w głównej pętli serwera:")
            traceback.print_exc()

        finally:
            if transport:
                transport.close()
            print("Serwer został zamknięty.")

class ServerProtocol(asyncio.DatagramProtocol):
    def __init__(self, server):
        self.server = server

    def datagram_received(self, data, addr):
        try:
            message = pickle.loads(data)

            if "disconnect" in message and message["disconnect"] is True:
                player_id = self.server.clients.pop(addr, None)
                if player_id:
                    self.server.level.players.pop(player_id, None)
                    self.server.inputs.pop(player_id, None)
                    print(f"Gracz {player_id} ({addr}) rozłączył się.")
                return

            if "player" in message:
                player = message["player"]
                self.server.register_client(addr, player)
            else:
                player_id = self.server.clients.get(addr)
                if player_id is None:
                    print(f"Nieznany klient {addr} wysłał dane bez rejestracji.")
                    return

                self.server.inputs[player_id] = message.get("keys", {})

                player = self.server.level.players.get(player_id)
                if player:
                    player.simulated_keys = self.server.inputs[player_id]
                    player.simulate_input(player.simulated_keys)

        except Exception as e:
            print(f"Błąd odbioru od {addr}: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(GameServer().start())
    except Exception as e:
        print("Błąd krytyczny przy uruchamianiu serwera:")
        traceback.print_exc()
        input("Naciśnij Enter, aby zamknąć...")