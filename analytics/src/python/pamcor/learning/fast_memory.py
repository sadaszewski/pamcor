import torch


class Transition(object):
    def __init__(self, state, action, next_state, reward):
        self.state = state
        self.action = action
        self.next_state = next_state
        self.reward = reward


class FastMemory(object):
    def __init__(self, max_size=10000):
        self.max_size = max_size
        self.actions = torch.empty(max_size, dtype=torch.long)
        self.rewards = torch.empty(max_size)
        self.states = None
        self.next_states = None
        self.count = 0
        self.index = 0

    def __len__(self):
        return self.count

    def lazy_init(self, state):
        if self.states is not None:
            return

        create = lambda: torch.empty((self.max_size,) + state.shape,
            dtype=state.dtype)

        self.states = create()
        self.next_states = create()

    def push(self, first, *rest): # state, next_state, action, reward):
        """
        append(state, next_state, action, reward)
          or
        append(transition)
        """
        if isinstance(first, Transition) and len(rest) == 0:
            state, next_state, action, reward = \
                first.state, first.next_state, first.action, first.reward
        elif len(rest) == 3:
            state, next_state, action, reward = (first,) + rest
        else:
            raise ValueError('Unrecognized argument list')

        self.lazy_init(state)
        index = self.index

        self.actions[index] = action
        self.rewards[index] = reward
        self.states[index, ...] = state
        self.next_states[index, ...] = next_state

        self.index = (self.index + 1) % self.max_size
        if self.count < self.max_size:
            self.count += 1

    def sample(self, size=100):
        index = torch.randperm(self.count)
        index = index[:size]
        states = self.states[index, ...]
        next_states = self.next_states[index, ...]
        actions = self.actions[index, ...]
        rewards = self.rewards[index, ...]
        return states, next_states, actions, rewards
