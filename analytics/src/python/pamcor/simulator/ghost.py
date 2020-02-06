from .entity import SimEntity
import numpy as np
from pamcor.common.maze import SOLID, BARRIER, \
    GHOST


class SimGhost(SimEntity):
    def __init__(self, sim_state, x, y, *args, **kwargs):
        super().__init__(sim_state, x, y, *args, **kwargs)
        self.game_start_pos = (x, y)
        self.entity_type = GHOST

    def is_cell_permeable(self, x, y, cell_type):
        if cell_type == SOLID:
            return False
        if cell_type != BARRIER:
            return True
        sim_state = self.sim_state
        if sim_state.power_pill_active:
            return True
        assert np.issubdtype(self.pos.dtype, np.integer)
        if self.pos[1] >= y:
            return True
        return False

    def take_action(self):
        if self.sim_state.power_pill_active:
            self.escape()
        else:
            self.pursue()

    def escape(self):
        dijkstra = self.sim_state.dijkstra
        x_0, y_0 = self.pos
        x_1, y_1 = self.game_start_pos
        dist, path, move_dir = \
            dijkstra.get_path(x_0, y_0, x_1, y_1)
        assert np.isfinite(dist)
        self.start_move(*move_dir)

    def pursue(self):
        player, dijkstra = self.sim_state.player, \
            self.sim_state.dijkstra
        x_0, y_0 = self.pos
        x_1, y_1 = player.pos.round().astype(np.int)
        is_valid, (x_1, y_1) = player.is_move_valid(0, 0)
        assert is_valid
        dist, path, move_dir = \
            dijkstra.get_path(x_0, y_0, x_1, y_1)
        assert np.isfinite(dist)
        print('x_0:', x_0, 'y_0:', y_0,
            'x_1:', x_1, 'y_1:', y_1,
            'move_dir:', move_dir)
        self.start_move(*move_dir)

    def die(self):
        self.pos = self.action_end_pos = \
            self.action_start_pos = \
            np.array(self.game_start_pos)
        self.move_dir = None
        # self.take_action()


def create_ghosts(sim_state):
    data = sim_state.maze.get_data()
    y, x = np.where(data == GHOST)
    res = [SimGhost(sim_state, x[i], y[i], (i + 1) * 0.1) \
        for i in range(len(x))]
    return res
