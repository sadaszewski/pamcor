#
# Copyright (C) Stanislaw Adaszewski, 2018
#

from pamcor.common.behavior_metrics import C4_CaughtAfterHunt
from pamcor.common import GameplaySample, \
    DijkstraDistances, \
    Maze


def test_01_caught():
    sample_feed = {
        'player_pos': (4, 29),
        'ghost_pos': [(1, 29), (12, 29)],
        'victory': False
    }

    metric = C4_CaughtAfterHunt()

    metric.apply(GameplaySample(t=0, power_pill_active=True,
        player_dead=False, **sample_feed))

    metric.apply(GameplaySample(t=1, power_pill_active=False,
        player_dead=False, **sample_feed))

    metric.apply(GameplaySample(t=16, power_pill_active=False,
        player_dead=True, **sample_feed))

    assert metric.value == 1


def test_02_not_caught():
    sample_feed = {
        'player_pos': (4, 29),
        'ghost_pos': [(1, 29), (12, 29)],
        'victory': False
    }

    metric = C4_CaughtAfterHunt()

    metric.apply(GameplaySample(t=0, power_pill_active=True,
        player_dead=False, **sample_feed))

    metric.apply(GameplaySample(t=1, power_pill_active=False,
        player_dead=False, **sample_feed))

    metric.apply(GameplaySample(t=16, power_pill_active=False,
        player_dead=False, **sample_feed))

    assert metric.value == 0


def test_03_no_power_pill():
    sample_feed = {
        'player_pos': (4, 29),
        'ghost_pos': [(1, 29), (12, 29)],
        'power_pill_active': False,
        'victory': False
    }

    metric = C4_CaughtAfterHunt()

    metric.apply(GameplaySample(t=0,
        player_dead=False, **sample_feed))

    metric.apply(GameplaySample(t=1,
        player_dead=False, **sample_feed))

    metric.apply(GameplaySample(t=16,
        player_dead=True, **sample_feed))

    assert metric.value == 0
