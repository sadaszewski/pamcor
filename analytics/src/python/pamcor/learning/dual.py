import numpy as np
from .memory import Transition
from torch import Tensor, no_grad, tensor
from torch.nn.functional import smooth_l1_loss
from torch.optim import RMSprop
from typing import List
import sys


class DualDQN(object):
    def __init__(self, net, eps_start=1.0,
        eps_end=0.1, eps_steps=1250000,
        policy_steps=10):
        self.n_actions = net.n_actions
        self.gamma = net.gamma
        self.target_net = net.clone()
        self.policy_net = net.clone()
        self.optimizer = None
        self.update_step_count = 0
        self.eps_step_count = 0
        self.policy_steps = policy_steps
        self.eps_start = eps_start
        self.eps_end = eps_end
        self.eps_steps = eps_steps

    def loss(self, tran: Transition) -> Tensor:
        state, action, next_state, reward = \
            tran.state, tran.action, tran.next_state, \
            tran.reward

        q_state = self.policy_net.forward(state)
        q_next_state = self.target_net.forward(next_state).detach()
        expected_q = self.gamma * q_next_state + reward
        loss = smooth_l1_loss(q_state, expected_q)

        return loss

    def get_optimizer(self):
        if self.optimizer is None:
            self.optimizer = RMSprop(params=self.policy_net.optim_params())
        return self.optimizer

    def learn_one(self, tran: Transition) -> None:
        loss = self.loss(tran)
        optimizer = self.get_optimizer()
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

    def learn(self, transitions: List[Transition]) -> None:
        sys.stdout.write('Learning: ')
        sys.stdout.flush()
        for i, tran in enumerate(transitions):
            if i and i % 10 == 0:
                sys.stdout.write(f' {i}')
                sys.stdout.flush()
            self.learn_one(tran)
        print()

        self.update_step_count += 1

        if self.update_step_count % self.policy_steps == 0:
            self.update_target_net()

    def learn_vectorized(self, transitions: List[Transition]) -> None:
        print('learn_vectorized() : ENTER')
        def get(name):
            return tensor(list(map(lambda a: getattr(a, name), transitions)))
        states, next_states, rewards, actions = \
            (get(a) for a in ['state', 'next_state', 'reward', 'action'])
        print('states.shape:', states.shape)
        print('next_states.shape:', next_states.shape)
        print('rewards.shape:', rewards.shape)
        print('actions.shape:', actions.shape)
        q_states = self.policy_net.forward(states)
        print('1 q_states.shape:', q_states.shape)
        q_states = q_states.gather(1, actions.view(-1, 1))
        print('2 q_states.shape:', q_states.shape)
        q_next_states = self.target_net.forward(next_states).detach()
        q_next_states, _ = q_next_states.max(1)
        print('q_next_states.shape:', q_next_states.shape)
        q_expected = self.gamma * q_next_states + rewards
        loss = smooth_l1_loss(q_states, q_expected)
        optimizer = self.get_optimizer()
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        print('learn_vectorized() : EXIT')

    def learn_fast(self, states, next_states, actions, rewards) -> None:
        print('learn_fast() : ENTER')
        print('states.shape:', states.shape)
        print('next_states.shape:', next_states.shape)
        print('rewards.shape:', rewards.shape)
        print('actions.shape:', actions.shape)
        q_states = self.policy_net.forward(states)
        print('1 q_states.shape:', q_states.shape)
        q_states = q_states.gather(1, actions.view(-1, 1))
        print('2 q_states.shape:', q_states.shape)
        q_next_states = self.target_net.forward(next_states).detach()
        q_next_states, _ = q_next_states.max(1)
        print('q_next_states.shape:', q_next_states.shape)
        q_expected = self.gamma * q_next_states + rewards
        loss = smooth_l1_loss(q_states, q_expected)
        optimizer = self.get_optimizer()
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        print('learn_fast() : EXIT')

    def update_target_net(self):
        print('Updating target_net ...')
        self.target_net = self.policy_net.clone()

    def select_action(self, state):
        eps = self.eps_end \
            if self.eps_step_count > self.eps_steps \
            else self.eps_start + self.eps_step_count * \
                (self.eps_end - self.eps_start) / self.eps_steps
        self.eps_step_count += 1
        with no_grad():
            best_action = self.policy_net.best_action(state)
        random_action = np.random.randint(0, self.n_actions)
        random_number = np.random.random()
        if random_number < eps:
            return random_action
        else:
            return best_action
