import os
import pickle
import numpy as np
from queue import PriorityQueue
from pamcor.common.maze import SOLID


class SimDijkstra(object):
    def __init__(self, maze):
        self.maze = maze
        self.maze_data = self.maze.get_data()
        self.accessible = (self.maze_data != SOLID)
        fname = maze.filename
        path, name = os.path.split(fname)
        name, ext = os.path.splitext(name)
        cache_fname = os.path.join(path, f'{name}_simdij.pickle')
        if os.path.exists(cache_fname):
            with open(cache_fname, 'rb') as f:
                self.cache = pickle.load(f)
        else:
            self.compute()
            with open(cache_fname, 'wb') as f:
                pickle.dump(self.cache, f)

    def compute(self):
        y, x = np.where(self.accessible)
        self.cache = {}
        print('Pre-computing Dijkstra distances and predecessors ...')
        for i in range(len(y)):
            if i and i % 100 == 0: print(i, end='\r')
            k = (x[i], y[i])
            distances, predecessors = self.dijkstra_slow(*k)
            self.cache[k] = (distances, predecessors)

    def get_path(self, x_0, y_0, x_1, y_1):
        if x_0 == x_1 and y_0 == y_1:
            return 0, [(x_0, y_0)], (0, 0)
        k_0 = (x_0, y_0)
        if k_0 not in self.cache:
            return np.inf, None, None
        distances, predecessors = self.cache[k_0]
        dist = distances[y_1, x_1]
        if dist == np.inf:
            return np.inf, None, None
        path = [(x_1, y_1)]
        p = predecessors[y_1, x_1]
        while p is not None:
            path.append(p)
            p = predecessors[p[1], p[0]]
        path.reverse()
        move_dir = np.array(path[1]) - k_0
        return dist, path, move_dir

    def dijkstra_slow(self, x, y):
        maze = self.maze
        maze_width = maze.width()
        maze_height = maze.height()
        maze_data = maze.get_data()
        accessible = self.accessible

        if x < 0 or x >= maze_width:
            raise ValueError('x out of range: %s' % x)
        if y < 0 or y >= maze_height:
            raise ValueError('y out of range: %s' % y)

        distances = np.ones((maze_height, maze_width)) * np.inf
        predecessors = np.empty(distances.shape, dtype=np.object)
        distances[y, x] = 0

        Q = PriorityQueue()
        Q.put_nowait((0, x, y))

        while not Q.empty():
            d, x, y = Q.get_nowait()
            for (x_1, y_1) in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                if x_1 < 0 or x_1 >= maze_width: continue
                if y_1 < 0 or y_1 >= maze_height: continue
                if not accessible[y_1, x_1]: continue
                if d + 1 < distances[y_1, x_1]:
                    distances[y_1, x_1] = d + 1
                    predecessors[y_1, x_1] = (x, y)
                    Q.put_nowait((d + 1, x_1, y_1))

        return distances, predecessors
