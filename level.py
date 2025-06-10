from game_config import SCREEN_WIDTH, SCREEN_HEIGHT

class Level:
    def __init__(self):
        self.walls = []
        self.players = {}
        self.enemies = []
        self.bullets = []

    def add_wall(self, wall):
        self.walls.append(wall)

    def add_player(self, player_id, player):
        self.players[player_id] = player

    def add_enemy(self, enemy):
        self.enemies.append(enemy)

    def update(self, delta_time):
        for player in self.players.values():
            player.movement(delta_time, self.walls)
        for enemy in self.enemies:
            enemy.movement(delta_time, self.walls)
        for bullet in self.bullets:
            bullet.move(delta_time)
            bullet.check_collision(self.walls, self.players, self.enemies)
        self.bullets = [b for b in self.bullets if b.alive]