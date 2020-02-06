#
# Copyright (C) Stanislaw Adaszewski, 2018
#

from pamcor.common import Maze, \
    GameplaySample, \
    DijkstraDistances
from pamcor.common.maze import PLAYER, \
    PILL
import numpy as np


def test_01_maze_dijkstra():
    maze = Maze.from_file('data/maze/maze0.txt')
    maze.dijkstra_precompute()

    t = 0

    x, y = player_pos = (13, 23)
    assert maze.maze[y, x] == PLAYER

    ghost_pos = [ (6, 20) ]
    x, y = ghost_pos[0]
    assert maze.maze[y, x] == PILL

    power_pill_active = False
    player_dead = False
    victory = False

    sample = GameplaySample(t, player_pos, ghost_pos, power_pill_active,
        player_dead, victory)

    for i in range(100):
        distances = maze.dijkstra(*player_pos)
        # print(distances)
        x, y = ghost_pos[0]
        assert distances[y, x] == 10

def test_02_dijkstra_distances():
    maze = Maze.from_file('data/maze/maze0.txt')
    maze.dijkstra_precompute()

    t = 0

    x, y = player_pos = (13, 23)
    assert maze.maze[y, x] == PLAYER

    ghost_pos = [ (6, 20), (21, 9), (1, 2) ]
    for i in range(3):
        x, y = ghost_pos[i]
        assert maze.maze[y, x] == PILL

    power_pill_active = False
    player_dead = False
    victory = False

    sample = GameplaySample(t, player_pos, ghost_pos, power_pill_active,
        player_dead, victory)

    distances = DijkstraDistances.from_maze_and_sample(maze, sample)

    assert distances.player_to_ghost[0] == 10
    assert distances.player_to_ghost[1] == 22
    assert distances.player_to_ghost[2] == 33

    assert distances.barrier_to_player == 21

    # print(distances)
    # x, y = ghost_pos[0]
    # assert distances[y, x] == 10
    assert distances.barrier_to_ghost[0] == 17
    assert distances.barrier_to_ghost[1] == 16
    assert distances.barrier_to_ghost[2] == 22


def test_03_dijkstra_barrier():
    maze = Maze.from_file('data/maze/maze0.txt')
    maze.dijkstra_precompute()

    t = 0

    x, y = player_pos = (13, 23)
    assert maze.maze[y, x] == PLAYER

    ghost_pos = [ (6, 20) ]
    x, y = ghost_pos[0]
    assert maze.maze[y, x] == PILL

    power_pill_active = False
    player_dead = False
    victory = False

    sample = GameplaySample(t, player_pos, ghost_pos, power_pill_active,
        player_dead, victory)

    barrier_x = np.array([13, 14])
    barrier_y = np.array([12, 12])

    distances = maze.dijkstra(barrier_x, barrier_y)
    print(distances)
    x, y = player_pos
    assert distances[y, x] == 21
