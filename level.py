from game_config import SCREEN_WIDTH, SCREEN_HEIGHT, font

class Level:
    def __init__(self):
        self.walls = []
        self.players = []

    def add_wall(self, wall):
        self.walls.append(wall)

    def add_player(self, player):
        self.players.append(player)

    def update(self, delta_time):
        for player in self.players:
            player.movement(delta_time, self.walls)

    def draw(self, surface, player_index):
        if not (0 <= player_index < len(self.players)):
            raise ValueError("Nieprawidłowy indeks gracza")

        observer = self.players[player_index]
        cam_x = observer.camera_x
        cam_y = observer.camera_y

        surface.fill((30, 30, 30))

        for wall in self.walls:
            wall.draw(surface, cam_x, cam_y)

        for p in self.players:
            p.draw(surface, cam_x, cam_y)

        pos_text = font.render(f"x: {int(observer.x)}  y: {int(observer.y)}", True, (255, 255, 255))
        surface.blit(pos_text, (10, 10))