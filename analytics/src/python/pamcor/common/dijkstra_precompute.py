#
# Copyright (C) Stanislaw Adaszewski, 2018
#

import numpy as np

class DijkstraPrecompute(object):
    def __init__(self, maze):
        self.maze = maze
        self.cache = {}

    def run(self):
        accessible = self.maze.accessible_mask()
        y, x = np.where(accessible)
        print('Pre-computing Dijkstra distances ...')
        for i in range(len(y)):
            if i and i % 100 == 0: print(i, end='\r')
            distances = self.maze.dijkstra_slow(x[i], y[i])
            k = (x[i], y[i])
            self.cache[k] = distances
        print()

    def dijkstra(self, x, y):
        try:
            iter(x)
        except TypeError:
            x = [x]
        try:
            iter(y)
        except TypeError:
            y = [y]

        res = self.cache[(x[0], y[0])]
        for i in range(1, len(x)):
            tmp = self.cache[(x[i], y[i])]
            res = np.min([res, tmp], axis=0)
        return res
