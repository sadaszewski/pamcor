import numpy as np


class Transition(object):
    def __init__(self, state, action, next_state, reward):
        self.state = state
        self.action = action
        self.next_state = next_state
        self.reward = reward


class ReplayMemory(object):
    def __init__(self, max_size=1000000):
        self.data = np.empty(max_size, dtype=np.object)
        self.index = 0
        self.n_used = 0
        self.max_size = max_size

    def push(self, item):
        # item = Transition(*args)
        self.data[self.index] = item
        self.index = (self.index + 1) % \
            self.max_size
        if self.n_used < self.max_size:
            self.n_used += 1

    def sample(self, size=100):
        perm = np.random.permutation(self.n_used)
        res = self.data[perm[:size]]
        return res

    def __len__(self):
        return self.n_used
