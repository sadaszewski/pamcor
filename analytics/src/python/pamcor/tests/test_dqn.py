from pamcor.learning.dqn import DeepQLearning
import numpy as np
import torch

def test_01_forward():
    dqn = DeepQLearning(n_actions=3)
    state = np.random.random((4, 128, 128))
    actions = dqn.forward(state)
    assert actions.shape == (1, 3)
    print('actions:', actions)
    with torch.no_grad():
        actions_1 = dqn.forward(state)
    assert (actions == actions_1).all()
    print('Weights:')
    print('cv1:')
    print(dqn.cv1.weight)
    print('cv2:')
    print(dqn.cv2.weight)
    print('cv3:')
    print(dqn.cv3.weight)
    print('dense:')
    print(dqn.dense.weight)
    print('actions:')
    print(dqn.actions.weight)


def test_02_best_action():
    dqn = DeepQLearning(n_actions=3)
    state = np.random.random((4, 128, 128))
    best_action = dqn.best_action(state)
    print('best_action:', best_action)
    assert best_action.shape == tuple()


def test_03_why_so_big():
    dqn = DeepQLearning(n_actions=3)
    state = np.random.random((4, 128, 128))
    actions = dqn.forward(state)

    y = dqn.cv1(state)
    print('after cv1:', y.shape, y)
    y = dqn.cv2(y)
    print('after cv2:', y.shape, y)
