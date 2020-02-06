from .player import SimPlayer, \
    create_player
from .ghost import create_ghosts
from .dijkstra import SimDijkstra


class SimState(object):
    def __init__(self, maze, player_class=SimPlayer):
        self.maze = maze
        self.t = 0
        self.power_pill_active = False
        self.player_dead = False
        self.victory = False

        self.player = create_player(self, player_class)
        self.ghosts = create_ghosts(self)
        self.entities = [self.player] + \
            self.ghosts
        self.dijkstra = SimDijkstra(maze)

        for e in self.entities:
            e.kickstart()

    def update(self, time_delta):
        for e in self.entities:
            e.update(time_delta)
