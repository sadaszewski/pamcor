#
# Copyright (C) Stanislaw Adaszewski, 2018
#

class GameState(object):
    def __init__(self):
        pass


class GameplaySample(object):
    def __init__(self, t, player_pos, ghost_pos, power_pill_active,
        player_dead, victory):
        self.t = t
        self.player_pos = player_pos
        self.ghost_pos = ghost_pos
        self.power_pill_active = power_pill_active
        self.player_dead = player_dead
        self.victory = victory
