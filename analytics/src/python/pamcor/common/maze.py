#
# Copyright (C) Stanislaw Adaszewski, 2018
#

import os
import numpy as np
from queue import PriorityQueue
from .dijkstra_precompute import DijkstraPrecompute
import pickle


_SOLID = 'hABCD=-IHi1234eEabcd'
_PILL = ' '
_POWER_PILL = '*'
_EMPTY = 'x'
_GHOST = '^'
_PLAYER = '<'
_BARRIER = '/'
_ALL = _SOLID + _PILL + _POWER_PILL + _EMPTY + \
    _GHOST + _PLAYER + _BARRIER + '\r\n'

SOLID = 1
PILL = 2
POWER_PILL = 3
EMPTY = 4
GHOST = 5
PLAYER = 6
BARRIER = 7

TILE_CHARS = {
    SOLID: _SOLID, PILL: _PILL, POWER_PILL: _POWER_PILL,
    EMPTY: _EMPTY, GHOST: _GHOST, PLAYER: _PLAYER,
    BARRIER: _BARRIER
}

CHAR_TO_TILE_TYPE = {}

for k, v in TILE_CHARS.items():
    for c in v:
        CHAR_TO_TILE_TYPE[c] = k

TILE_NAMES = {
    SOLID: 'solid',
    PILL: 'pill',
    POWER_PILL: 'power_pill',
    EMPTY: 'empty',
    GHOST: 'ghost',
    PLAYER: 'player',
    BARRIER: 'barrier'
}


# A============HH============D
# I            ii            I
# I 1--4 1---4 ii 1---4 1--4 I
# I*ixxi ixxxi ii ixxxi ixxi*I
# I 2--3 2---3 23 2---3 2--3 I
# I                          I
# I 1--4 14 1------4 14 1--4 I
# I 2--3 ii 2--41--3 ii 2--3 I
# I      ii    ii    ii      I
# b----4 i2--4 ii 1--3i 1----c
# xxxxxi i1--3x23x2--4i ixxxxx
# xxxxxi iixxxxxxxxxxii ixxxxx
# xxxxxi iix1--//--4xii ixxxxx
# -----3 23xixxxxxxix23 2-----
# xxxxxx xxxix^x^x^ixxx xxxxxx
# -----4 14xixxxxxxix14 1-----
# xxxxxi iix2------3xii ixxxxx
# xxxxxi iixxxxxxxxxxii ixxxxx
# xxxxxi iix1------4xii ixxxxx
# a----3 23x2--41--3x23 2----d
# I            ii            I
# I 1--4 1---4 ii 1---4 1--4 I
# I 2-4i 2---3 23 2---3 i1-3 I
# I*  ii       <        ii  *I
# E-4 ii 14 1------4 14 ii 1-e
# E-3 23 ii 2--41--3 ii 23 2-e
# I      ii    ii    ii      I
# I 1----32--4 ii 1--32----4 I
# I 2--------3 23 2--------3 I
# I                          I
# B==========================C

MAZE_WIDTH = 28
MAZE_HEIGHT = 31

class Maze(object):
    @staticmethod
    def from_file(fname):
        with open(fname, 'r') as f:
            data = f.read()
        for i, c in enumerate(data):
            if c not in _ALL:
                raise ValueError('Invalid characters encountered: %s at %d' % \
                    (c, i))
        maze = []
        row = []

        def add_row():
            if len(row) < MAZE_WIDTH:
                raise ValueError('Row too short')
            maze.append(row)
            if len(maze) > MAZE_HEIGHT:
                raise ValueError('Too many rows')

        for c in data:
            if c == '\r': continue
            if c == '\n':
                add_row()
                row = []
                continue
            tt = CHAR_TO_TILE_TYPE[c]
            row.append(tt)
            if len(row) > MAZE_WIDTH:
                raise ValueError('Row too long')
        if len(row) > 0:
            add_row()
        if len(maze) < MAZE_HEIGHT:
            raise ValueError('Too few rows: %d' % len(maze))

        res = Maze(maze)
        res.precompute = DijkstraPrecompute(res)
        res.filename = fname

        path, name = os.path.split(fname)
        name, ext = os.path.splitext(name)
        dij_fname = os.path.join(path, name + '_dijkstra.pickle')
        # print('dij_fname:', dij_fname)
        if os.path.exists(dij_fname):
            with open(dij_fname, 'rb') as f:
                cache = pickle.load(f)
            res.precompute.cache = cache
        else:
            res.precompute.run()
            with open(dij_fname, 'wb') as f:
                pickle.dump(res.precompute.cache, f)

        return res

    def __init__(self, maze):
        self.maze = np.array(maze)
        self.precompute = None

    def get_data(self):
        return self.maze

    def get_size(self):
        return np.array([self.width(), self.height()])

    def tile_type_count(self, tt):
        return np.sum(self.maze == tt)

    def accessible_mask(self):
        accessible = (self.maze != SOLID) # * (self.maze != EMPTY)
        return accessible

    def dijkstra_precompute(self):
        # self.precompute = DijkstraPrecompute(self)
        # self.precompute.run()
        pass

    def dijkstra(self, x, y):
        if self.precompute is None:
            return self.dijkstra_slow(x, y)
        return self.precompute.dijkstra(x, y)

    def dijkstra_slow(self, x, y):
        try:
            iter(x)
        except TypeError:
            x = np.array([x])
        try:
            iter(y)
        except TypeError:
            y = np.array([y])
        if any(x < 0) or any(x >= MAZE_WIDTH):
            raise ValueError('x out of range: %s' % x)
        if any(y < 0) or any(y >= MAZE_HEIGHT):
            raise ValueError('y out of range: %s' % y)
        accessible = (self.maze != SOLID) # * (self.maze != EMPTY)
        distances = np.ones((MAZE_HEIGHT, MAZE_WIDTH)) * np.inf
        # visited = np.zeros((MAZE_HEIGHT, MAZE_WIDTH), dtype=np.bool)
        distances[y, x] = 0
        Q = PriorityQueue()
        for i in range(len(x)):
            Q.put_nowait((0, x[i], y[i]))
        while not Q.empty():
            d, x, y = Q.get_nowait()
            # if visited[y, x]: continue
            # visited[y, x] = True
            for (x_1, y_1) in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                if x_1 < 0 or x_1 >= MAZE_WIDTH: continue
                if y_1 < 0 or y_1 >= MAZE_HEIGHT: continue
                if not accessible[y_1, x_1]: continue
                if d + 1 < distances[y_1, x_1]:
                    distances[y_1, x_1] = d + 1
                    Q.put_nowait((d + 1, x_1, y_1))
        return distances

    def width(self):
        return MAZE_WIDTH

    def height(self):
        return MAZE_HEIGHT

    def trapped_by_ghosts(self, player_pos, ghost_pos, max_dist=20):
        accessible = (self.maze != SOLID)
        for x, y in map(lambda a: map(round, a[:2]), ghost_pos):
            accessible[y, x] = False
        distances = np.ones((MAZE_HEIGHT, MAZE_WIDTH)) * np.inf
        x, y = map(round, player_pos[:2])
        distances[y, x] = 0
        Q = PriorityQueue()
        Q.put_nowait((0, x, y))
        longest = 0
        while not Q.empty():
            d, x, y = Q.get_nowait()
            for (x_1, y_1) in ((x - 1, y), (x + 1, y), (x, y - 1), (x, y + 1)):
                if x_1 < 0 or x_1 >= MAZE_WIDTH: continue
                if y_1 < 0 or y_1 >= MAZE_HEIGHT: continue
                if not accessible[y_1, x_1]: continue
                d_1 = d + 1
                if d_1 <= max_dist and \
                    d_1 < distances[y_1, x_1]:
                    longest = max(longest, d_1)
                    distances[y_1, x_1] = d_1
                    Q.put_nowait((d_1, x_1, y_1))
        return longest
