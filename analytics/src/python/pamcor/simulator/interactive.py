import numpy as np
from PIL import Image
from pamcor.common import Maze
from .draw import draw_state
import cv2
from .state import SimState
import time


def game_timestep(maze, player_input, time_delta=0.01):
    pass


def main(maze, args):
    # maze = Maze.from_file('data/maze/maze0.txt')
    sim_state = SimState(maze)
    player = sim_state.player
    wndname = 'pamcorsim'
    cv2.namedWindow(wndname)
    scale = 20
    timestamp = time.time()
    next_move_dir = None
    while True:
        t = time.time()
        time_delta = t - timestamp
        timestamp = t
        sim_state.update(time_delta)
        im, _ = draw_state(sim_state,
            maze.width() * scale,
            maze.height() * scale)
        # for _ in range(4):
            # im = gaussian_filter(im, 5)
        cv2.imshow(wndname, im)
        key = cv2.waitKey(25)
        # print('key:', key)
        if key == ord('a'):
            next_move_dir = (-1, 0)
        elif key == ord('d'):
            next_move_dir = (1, 0)
        elif key == ord('w'):
            next_move_dir = (0, -1)
        elif key == ord('s'):
            next_move_dir = (0, 1)
        elif key == 27:
            break
        if next_move_dir is not None:
            is_valid, _ = player.will_move_be_valid(*next_move_dir)
            if is_valid:
                player.next_move_dir = next_move_dir
        # pil_im.save('draw_maze_test.png')
        if sim_state.player_dead:
            print('Player died')
            break
        if sim_state.victory:
            print('You win!')
            break
