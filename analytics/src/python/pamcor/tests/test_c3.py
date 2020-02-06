#
# Copyright (C) Stanislaw Adaszewski, 2018
#

from pamcor.common.behavior_metrics import C3_CloseCalls
from pamcor.common import GameplaySample, \
    DijkstraDistances, \
    Maze


def test_01_killed():
    sample_feed = {
        'player_pos': (4, 29),
        'ghost_pos': [(1, 29), (12, 29)],
        'victory': False,
        'power_pill_active': False
    }

    distances_feed = {
        'barrier_to_player': 5,
        'barrier_to_ghost': [5, 5]
    }

    metric = C3_CloseCalls()

    metric.apply(GameplaySample(t=0, player_dead=False, **sample_feed),
        distances=DijkstraDistances(player_to_ghost=[1, 10], **distances_feed))

    metric.apply(GameplaySample(t=1, player_dead=False, **sample_feed),
        distances=DijkstraDistances(player_to_ghost=[2, 10], **distances_feed))

    metric.apply(GameplaySample(t=5, player_dead=True, **sample_feed),
        distances=DijkstraDistances(player_to_ghost=[0, 10], **distances_feed))

    assert metric.value == 0


def test_02_close_call():
    sample_feed = {
        'player_pos': (4, 29),
        'ghost_pos': [(1, 29), (12, 29)],
        'victory': False,
        'power_pill_active': False
    }

    distances_feed = {
        'barrier_to_player': 5,
        'barrier_to_ghost': [5, 5]
    }

    metric = C3_CloseCalls()

    metric.apply(GameplaySample(t=0, player_dead=False, **sample_feed),
        distances=DijkstraDistances(player_to_ghost=[1, 10], **distances_feed))

    metric.apply(GameplaySample(t=1, player_dead=False, **sample_feed),
        distances=DijkstraDistances(player_to_ghost=[2, 10], **distances_feed))

    metric.apply(GameplaySample(t=5, player_dead=False, **sample_feed),
        distances=DijkstraDistances(player_to_ghost=[0, 10], **distances_feed))

    assert metric.value == 1


def test_03_not_close():
    sample_feed = {
        'player_pos': (4, 29),
        'ghost_pos': [(1, 29), (12, 29)],
        'victory': False,
        'power_pill_active': False
    }

    distances_feed = {
        'barrier_to_player': 5,
        'barrier_to_ghost': [5, 5]
    }

    metric = C3_CloseCalls()

    metric.apply(GameplaySample(t=0, player_dead=False, **sample_feed),
        distances=DijkstraDistances(player_to_ghost=[2, 10], **distances_feed))

    metric.apply(GameplaySample(t=1, player_dead=False, **sample_feed),
        distances=DijkstraDistances(player_to_ghost=[3, 10], **distances_feed))

    metric.apply(GameplaySample(t=5, player_dead=False, **sample_feed),
        distances=DijkstraDistances(player_to_ghost=[1, 10], **distances_feed))

    assert metric.value == 0


def test_04_on_power_pill():
    sample_feed = {
        'player_pos': (4, 29),
        'ghost_pos': [(1, 29), (12, 29)],
        'victory': False,
        'power_pill_active': True
    }

    distances_feed = {
        'barrier_to_player': 5,
        'barrier_to_ghost': [5, 5]
    }

    metric = C3_CloseCalls()

    metric.apply(GameplaySample(t=0, player_dead=False, **sample_feed),
        distances=DijkstraDistances(player_to_ghost=[1, 10], **distances_feed))

    metric.apply(GameplaySample(t=1, player_dead=False, **sample_feed),
        distances=DijkstraDistances(player_to_ghost=[2, 10], **distances_feed))

    metric.apply(GameplaySample(t=5, player_dead=False, **sample_feed),
        distances=DijkstraDistances(player_to_ghost=[0, 10], **distances_feed))

    assert metric.value == 0
