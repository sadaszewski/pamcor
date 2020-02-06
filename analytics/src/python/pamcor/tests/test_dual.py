from pamcor.learning.dual import DualDQN
from pamcor.learning.dqn import DeepQLearning
from pamcor.learning.memory import Transition
import numpy as np
from torch.optim import RMSprop


def test_01_create():
    dqn = DeepQLearning(n_actions=4)
    dual_dqn = DualDQN(dqn)
    assert dual_dqn.policy_net is not None
    assert dual_dqn.target_net is not None
    assert dual_dqn.policy_net != dual_dqn.target_net


def test_02_learn_one():
    dqn = DeepQLearning(n_actions=4)
    dual_dqn = DualDQN(dqn)

    state = np.random.random((4, 128, 128))
    next_state = np.random.random((4, 128, 128))
    action = 3
    reward = 5
    tran = Transition(state, action, next_state, reward)

    dual_dqn.learn_one(tran)

    for net in (dual_dqn.policy_net,
        dual_dqn.target_net):
        for param in net.optim_params():
            assert param is not None


def test_03_loss():
    dqn = DeepQLearning(n_actions=4)
    dual_dqn = DualDQN(dqn)

    state = np.random.random((4, 128, 128))
    next_state = np.random.random((4, 128, 128))
    action = 3
    reward = 5
    tran = Transition(state, action, next_state, reward)

    loss = dual_dqn.loss(tran)
    print('loss before:', loss)

    cv1_before = dual_dqn.policy_net.cv1.weight.clone().detach()

    params = dual_dqn.policy_net.optim_params()
    # print('params:', params)

    optimizer = RMSprop(params=params)
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

    loss = dual_dqn.loss(tran)
    print('loss after:', loss)

    cv1_after = dual_dqn.policy_net.cv1.weight.clone().detach()

    # print('cv1_before:', cv1_before)

    # print('cv1_after:', cv1_after)

    assert (cv1_before != cv1_after).any()

    # assert


def test_04_update():
    dqn = DeepQLearning(n_actions=4)
    dual_dqn = DualDQN(dqn, policy_steps=10)

    state = np.random.random((4, 128, 128))
    next_state = np.random.random((4, 128, 128))
    action = 3
    reward = 5
    tran = Transition(state, action, next_state, reward)

    for i in range(9):
        dual_dqn.learn([tran])

    print((dual_dqn.policy_net.cv1.weight == \
        dual_dqn.target_net.cv1.weight).all())

    print((dual_dqn.policy_net.cv2.weight == \
        dual_dqn.target_net.cv2.weight).all())

    #print(dual_dqn.target_net.cv1.weight)

    assert (dual_dqn.policy_net.cv1.weight != \
        dual_dqn.target_net.cv1.weight).any()

    dual_dqn.learn([tran])

    assert (dual_dqn.policy_net.cv1.weight == \
        dual_dqn.target_net.cv1.weight).all()


def test_05_select_action():
    dqn = DeepQLearning(n_actions=4)
    dual_dqn = DualDQN(dqn, eps_start=1.0,
        eps_end=1.0)

    state = np.random.random((4, 128, 128))
    actions = [dual_dqn.select_action(state) for i in range(100)]
    actions = np.array(actions)
    print('actions (random):', actions)
    # print(np.histogram(actions))
    assert (actions != actions[0]).any()

    dual_dqn = DualDQN(dqn, eps_start=0.0, eps_end=0.0)
    actions = [dual_dqn.select_action(state) for i in range(100)]
    actions = np.array(actions)
    print('actions (non-random):', actions)

    assert (actions == actions[0]).all()

    dual_dqn = DualDQN(dqn, eps_start=1.0, eps_end=0.0, eps_steps=50)
    actions = [dual_dqn.select_action(state) for i in range(100)]
    actions = np.array(actions)
    print('actions (eps-greedy):', actions)

    assert (actions[50:] == actions[50]).all()
    assert (actions[:50] != actions[0]).any()
