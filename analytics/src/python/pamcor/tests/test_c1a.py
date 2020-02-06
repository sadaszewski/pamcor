#
# Copyright (C) Stanislaw Adaszewski, 2018
#

from pamcor.common.behavior_metrics import C1a_TimesTrappedByGhosts
from pamcor.common import GameplaySample, \
    DijkstraDistances, \
    Maze


def test_01_trapped_by_ghosts():
    maze = Maze.from_file('data/maze/maze0.txt')

    sample_feed = {
        'power_pill_active': False,
        'player_pos': (4, 29),
        'ghost_pos': ((1, 29), (12, 29)),
        'player_dead': False,
        'victory': False
    }

    metric = C1a_TimesTrappedByGhosts()

    metric.apply(GameplaySample(t=0, **sample_feed), maze)

    metric.apply(GameplaySample(t=1, **sample_feed), maze)

    metric.apply(GameplaySample(t=2, **sample_feed), maze)

    metric.apply(GameplaySample(t=3, **sample_feed), maze)

    assert metric.value == 4


def test_02_not_trapped():
    maze = Maze.from_file('data/maze/maze0.txt')

    sample_feed = {
        'power_pill_active': False,
        'player_pos': (4, 29),
        'ghost_pos': ((1, 29), (13, 29)),
        'player_dead': False,
        'victory': False
    }

    metric = C1a_TimesTrappedByGhosts()

    metric.apply(GameplaySample(t=0, **sample_feed), maze)

    metric.apply(GameplaySample(t=1, **sample_feed), maze)

    metric.apply(GameplaySample(t=2, **sample_feed), maze)

    metric.apply(GameplaySample(t=3, **sample_feed), maze)

    assert metric.value == 0


def test_03_become_trapped():
    maze = Maze.from_file('data/maze/maze0.txt')

    sample_feed = {
        'power_pill_active': False,
        'player_pos': (4, 29),
        'player_dead': False,
        'victory': False
    }

    metric = C1a_TimesTrappedByGhosts()

    metric.apply(GameplaySample(t=0, ghost_pos=((1, 29), (13, 29)),
        **sample_feed), maze)

    metric.apply(GameplaySample(t=1, ghost_pos=((2, 29), (12, 29)),
        **sample_feed), maze)

    metric.apply(GameplaySample(t=2, ghost_pos=((1, 29), (11, 29)),
        **sample_feed), maze)

    metric.apply(GameplaySample(t=3, ghost_pos=((2, 29), (12, 29)),
        **sample_feed), maze)

    metric.apply(GameplaySample(t=3, ghost_pos=((1, 29), (13, 29)),
        **sample_feed), maze)

    assert metric.value == 3
