#
# Copyright (C) Stanislaw Adaszewski, 2018
#

from pamcor.common.maze import BARRIER
import numpy as np


class DijkstraDistances(object):
    @staticmethod
    def from_maze_and_sample(maze, sample):
        x, y = map(round, sample.player_pos[:2])
        distances = maze.dijkstra(x, y)
        player_to_ghost = []
        for i, gp in enumerate(sample.ghost_pos):
            (x, y) = map(round, gp[:2])
            player_to_ghost.append(distances[y, x])

        (y, x) = np.where(maze.maze == BARRIER)
        distances = maze.dijkstra(x, y)
        x, y = map(round, sample.player_pos[:2])
        barrier_to_player = distances[y, x]
        barrier_to_ghost = []
        for i, gp in enumerate(sample.ghost_pos):
            (x, y) = map(round, gp[:2])
            barrier_to_ghost.append(distances[y, x])

        return DijkstraDistances(player_to_ghost,
            barrier_to_player,
            barrier_to_ghost)

    def __init__(self, player_to_ghost,
        barrier_to_player,
        barrier_to_ghost):

        self.player_to_ghost = player_to_ghost
        self.barrier_to_player = barrier_to_player
        self.barrier_to_ghost = barrier_to_ghost
