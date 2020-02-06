import numpy as np
from pamcor.common.maze import SOLID, BARRIER, \
    PILL, POWER_PILL, PLAYER, GHOST


class SimEntity(object):
    def __init__(self, sim_state, x, y, traversal_time):
        self.sim_state = sim_state
        self.maze = sim_state.maze
        self.maze_data = self.maze.get_data()
        self.pos = np.array([x, y])
        self.traversal_time = traversal_time

        self.move_dir = None
        self.action_start_pos = None
        self.action_end_pos = None
        self.time_accum = None
        self.entity_type = None
        self.last_move_dir = None

    def is_cell_permeable(self, x, y, cell_type):
        raise NotImplemented

    def is_move_valid(self, dx, dy):
        pos = np.array(self.action_start_pos \
            if self.action_start_pos is not None \
            else self.pos).round().astype(np.int)
        return self.validate_move(pos, dx, dy)

    def will_move_be_valid(self, dx, dy):
        pos = np.array(self.action_end_pos \
            if self.action_end_pos is not None \
            else self.pos)
        return self.validate_move(pos, dx, dy)

    def validate_move(self, pos, dx, dy):
        pos = np.array(pos) + [dx, dy]
        maze = self.maze
        if dx not in [0, 1, -1]:
            return False, None
        if dy not in [0, 1, -1]:
            return False, None
        mask = (pos < 0)
        pos[mask] = (maze.get_size() - 1)[mask]
        mask = (pos >= maze.get_size())
        pos[mask] = np.array([0, 0])[mask]
        cell_x, cell_y = pos
        cell_type = self.maze_data[cell_y][cell_x]
        if not self.is_cell_permeable(cell_x, cell_y, cell_type):
            return False, None
        return True, pos

    def start_move(self, dx, dy):
        is_valid, end_pos = self.is_move_valid(dx, dy)
        assert is_valid
        assert dx in [0, 1, -1]
        assert dy in [0, 1, -1]
        self.move_dir = np.array([dx, dy])
        self.action_start_pos = np.array(self.pos)
        self.action_end_pos = end_pos
        self.time_accum = 0

    def update(self, time_delta):
        if self.move_dir is None:
            self.take_action()
            return

        self.last_move_dir = self.move_dir

        self.time_accum += time_delta
        finished = (self.time_accum >= self.traversal_time)
        ''' print('update(), time_delta:', time_delta,
            'time_accum:', self.time_accum,
            'traversal_time:', self.traversal_time,
            'move_dir:', self.move_dir,
            'action_start_pos:', self.action_start_pos,
            'finished:', finished) '''
        if finished:
            self.pos = self.action_end_pos
            self.action_end_pos = None
            self.action_start_pos = None
            self.move_dir = None
            self.move_finished()
            self.take_action()
        else:
            f = self.time_accum / self.traversal_time
            self.pos = self.action_start_pos + f * self.move_dir

    def move_finished(self):
        pass

    def take_action(self):
        raise NotImplemented

    def die(self):
        raise NotImplemented

    def kickstart(self):
        self.move_finished()
        self.take_action()

    def overlaps(self, other):
        x_0, y_0 = self.pos
        x_1, y_1 = other.pos
        print('overlaps() x_0:', x_0, 'y_0:', y_0,
            'x_1:', x_1, 'y_1:', y_1)
        if x_0 == x_1 and abs(y_0 - y_1) <= .5:
            return True
        if y_0 == y_1 and abs(x_0 - x_1) <= .5:
            return True
        return False
