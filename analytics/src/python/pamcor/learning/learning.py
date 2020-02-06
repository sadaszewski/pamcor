from pamcor.common import Maze
from pamcor.simulator import SimState, \
    draw_state
from pamcor.simulator.bitmaps import TILE_WIDTH, \
    TILE_HEIGHT
import cv2
import numpy as np
from .dqn import DeepQLearning
from .dual import DualDQN
from .fast_memory import FastMemory, \
    Transition
from .player import LearningPlayer
import pickle
import torch


WNDNAME = 'pamcorsim - Learning ...'
FRAME_TRAIL_LENGTH = 4
BATCH_SIZE = 100


def create_state(maze):
    sim_state = SimState(maze, player_class=LearningPlayer)
    player = sim_state.player
    return sim_state, player, None, None


def play_game(maze, memory, dual_dqn):
    sim_state, player, state, prev_state = \
        create_state(maze)
    time_delta = player.traversal_time / 4

    scale = 4
    frame_trail = []

    while True:
        sim_state.update(time_delta)

        im, _ = draw_state(sim_state,
            maze.width() * TILE_WIDTH,
            maze.height() * TILE_HEIGHT)

        frame_trail.append(im)
        if len(frame_trail) > FRAME_TRAIL_LENGTH:
            frame_trail.pop(0)

        im, _ = draw_state(sim_state,
            maze.width() * TILE_WIDTH * scale,
            maze.height() * TILE_HEIGHT * scale)

        cv2.imshow(WNDNAME, im)
        key = cv2.waitKey(50)
        if key == 27:
            break

        if len(frame_trail) < FRAME_TRAIL_LENGTH:
            continue

        input_ = np.array(frame_trail).astype(np.float32)
        input_ = torch.tensor(input_)

        action = dual_dqn.select_action(input_)
        player.press_button(action)

        state = (input_, player.score, action)

        reward = 0

        if sim_state.victory:
            reward += 500
            print('victory')

        if sim_state.player_dead:
            reward -= 500
            print('player_dead')

        if state is not None and prev_state is not None:
            prev_input, prev_score, prev_action = prev_state
            reward = time_delta + (player.score - prev_score)
            transition = Transition(prev_input, prev_action,
                input_, reward)
            memory.push(transition)

        prev_state = state

        if sim_state.player_dead or sim_state.victory:
            return

        if len(memory) >= BATCH_SIZE:
            dual_dqn.learn_fast(*memory.sample(BATCH_SIZE))


def main(maze, args):
    print('learning_main()')

    memory = FastMemory()
    dqn = DeepQLearning(n_actions=4)
    dual_dqn = DualDQN(dqn)

    cv2.namedWindow(WNDNAME)

    print('Learning ...')
    for i in range(100000):
        print('i:', i)
        play_game(maze, memory, dual_dqn)

    print('Saving the model ...')
    with open('dual_dqn_model.pickle', 'wb') as f:
        pickle.dump(dual_dqn, f)
