from .nn import Conv2D, Dense
from .memory import Transition
from torch.optim import RMSprop
from torch.nn.functional import smooth_l1_loss
import numpy as np
from typing import List


class DeepQLearning(object):
    def __init__(self, n_actions, gamma=0.1, eps=0.1, cv1=None, cv2=None, cv3=None,
        dense=None, actions=None):
        self.n_actions = n_actions
        self.gamma = gamma
        self.eps = eps
        self.cv1 = cv1 or Conv2D(32, kernel_size=8, stride=4)
        self.cv2 = cv2 or Conv2D(64, kernel_size=4, stride=2)
        self.cv3 = cv3 or Conv2D(64, kernel_size=3, stride=1)
        self.dense = dense or Dense(512)
        self.actions = actions or Dense(n_actions, activation=None)
        self.optimizer = None

    def optim_params(self):
        res = [self.cv1.weight,
            self.cv2.weight, self.cv3.weight,
            self.dense.weight, self.actions.weight]
        return res

    def clone(self):
        feed = {
            'cv1': self.cv1.clone(),
            'cv2': self.cv2.clone(),
            'cv3': self.cv3.clone(),
            'dense': self.dense.clone(),
            'actions': self.actions.clone()
        }
        res = DeepQLearning(self.n_actions, **feed)
        return res

    def forward(self, state):
        res = self.cv1(state)
        res = self.cv2(res)
        res = self.cv3(res)
        res = res.view(res.shape[0], -1)
        res = self.dense(res)
        res = self.actions(res)
        return res

    def best_action(self, state):
        res = self.forward(state)
        return np.argmax(res)

    def learn(self: None, transitions: List[Transition]) -> None:
        for tran in transitions:
            self.learn_one(tran)

    def learn_one(self: None, tran: Transition) -> None:
        state, action, next_state, reward = \
            tran.state, tran.action, tran.next_state, \
            tran.reward

        if self.optimizer is None:
            self.optimizer=RMSprop(params=self.optim_params())

        optimizer = self.optimizer

        q_state = self.forward(state)
        q_next_state = self.forward(next_state).detach()
        expected_q = self.gamma * q_next_state + reward

        loss = smooth_l1_loss(q_state, expected_q)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
