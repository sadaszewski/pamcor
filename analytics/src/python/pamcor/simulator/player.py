import numpy as np
from .entity import SimEntity
from pamcor.common.maze import SOLID, EMPTY, \
    PILL, POWER_PILL, PLAYER, BARRIER


NORMAL_SCORE_MULTIPLIER = 1
POWER_PILL_SCORE_MULTIPLIER = 2
PILL_SCORE = 100
POWER_PILL_SCORE = 500
POWER_PILL_DURATION = 5
EAT_GHOST_SCORE = 1000
PLAYER_TRAVERSAL_TIME = 0.1


class SimPlayer(SimEntity):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.score = 0
        self.next_move_dir = None
        self.entity_type = PLAYER
        self.total_pills = \
            np.sum(self.maze_data == PILL) + \
            np.sum(self.maze_data == POWER_PILL)
        self.eaten_pills = 0
        self.power_pill_time_accum = None
        self.eaten_ghosts = 0

    def is_cell_permeable(self, x, y, cell_type):
        if cell_type in {SOLID, BARRIER}:
            return False
        return True

    def update(self, time_delta):
        super().update(time_delta)

        if self.sim_state.power_pill_active:
            self.power_pill_time_accum += time_delta
            if self.power_pill_time_accum >= POWER_PILL_DURATION:
                self.sim_state.power_pill_active = False

        ghosts = self.sim_state.ghosts
        for g in ghosts:
            if g.overlaps(self):
                if self.sim_state.power_pill_active:
                    g.die()
                    self.score += EAT_GHOST_SCORE * (self.eaten_ghosts + 1)
                else:
                    self.die()

    def move_finished(self):
        x, y = self.pos
        cell_type = self.maze_data[y, x]

        score_multiplier = POWER_PILL_SCORE_MULTIPLIER \
            if self.sim_state.power_pill_active \
            else NORMAL_SCORE_MULTIPLIER

        if cell_type in {PILL, POWER_PILL}:
            self.maze_data[y, x] = EMPTY
            self.eaten_pills += 1
            if self.eaten_pills % 10 == 0:
                print('Eaten pills:', self.eaten_pills,
                    '/', self.total_pills)

        if cell_type == PILL:
            self.score += PILL_SCORE * score_multiplier
        elif cell_type == POWER_PILL:
            self.score += POWER_PILL_SCORE * score_multiplier
            self.sim_state.power_pill_active = True
            self.power_pill_time_accum = 0
            # self.maze_data[y, x] = EMPTY
            # self.eaten_pills += 1

        if self.eaten_pills == self.total_pills:
            self.sim_state.victory = True

    def take_action(self):
        # print('SimPlayer.take_action()')
        if self.next_move_dir is None:
            return

        dx, dy = self.next_move_dir
        # print('dx:', dx, 'dy:', dy)

        is_valid, end_pos = self.is_move_valid(dx, dy)
        # print('is_valid:', is_valid, 'end_pos:', end_pos)
        if not is_valid:
            return

        self.start_move(dx, dy)

    def die(self):
        self.sim_state.player_dead = True


def create_player(sim_state, player_class=SimPlayer):
    data = sim_state.maze.get_data()
    y, x = np.where(data == PLAYER)
    res = player_class(sim_state, x[0], y[0], PLAYER_TRAVERSAL_TIME)
    return res


class RandomPlayer(SimPlayer):
    def __init__(self, *args, **kwargs):
        # sim_state, x, y, traversal_time):
        super().__init__(*args, **kwargs)

    def take_action(self):
        is_valid, end_pos = self.is_move_valid(*self.last_move_dir) \
            if self.last_move_dir is not None \
            else (False, None)
        if is_valid:
            print('using last_move_dir:', self.last_move_dir,
                'is_valid:', is_valid,
                'end_pos:', end_pos)
            self.start_move(*self.last_move_dir)
            return
        choices = np.array([(0, 1), (0, -1), (-1, 0), (1, 0)],
            dtype=np.object)
        choices = choices[np.random.permutation(4)]
        for move_dir in choices:
            is_valid, _ = self.is_move_valid(*move_dir)
            if is_valid:
                self.start_move(*move_dir)
                return
