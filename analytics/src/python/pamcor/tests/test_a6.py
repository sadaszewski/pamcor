#
# Copyright (C) Stanislaw Adaszewski, 2018
#

from pamcor.common.behavior_metrics import A6_ChaseGhostsOrCollectDots
from pamcor.common import GameplaySample, \
    DijkstraDistances


def test_01_chase_ghosts():
    sample_feed = {
        'player_pos': None,
        'ghost_pos': None,
        'player_dead': False,
        'victory': False
    }

    dist_feed = {
        'barrier_to_player': [20],
        'barrier_to_ghost': [19]
    }

    metric = A6_ChaseGhostsOrCollectDots()

    metric.apply(GameplaySample(t=0, power_pill_active=True, **sample_feed),
        DijkstraDistances(player_to_ghost=[10], **dist_feed))

    metric.apply(GameplaySample(t=1, power_pill_active=True, **sample_feed),
        DijkstraDistances(player_to_ghost=[9], **dist_feed))

    metric.apply(GameplaySample(t=2, power_pill_active=True, **sample_feed),
        DijkstraDistances(player_to_ghost=[9], **dist_feed))

    metric.apply(GameplaySample(t=3, power_pill_active=True, **sample_feed),
        DijkstraDistances(player_to_ghost=[8], **dist_feed))

    assert metric.value == 2


def test_02_collect_dots():
    sample_feed = {
        'player_pos': None,
        'ghost_pos': None,
        'player_dead': False,
        'victory': False
    }

    dist_feed = {
        'barrier_to_player': [20],
        'barrier_to_ghost': [19]
    }

    metric = A6_ChaseGhostsOrCollectDots()

    metric.apply(GameplaySample(t=0, power_pill_active=True, **sample_feed),
        DijkstraDistances(player_to_ghost=[10], **dist_feed))

    metric.apply(GameplaySample(t=1, power_pill_active=True, **sample_feed),
        DijkstraDistances(player_to_ghost=[10], **dist_feed))

    metric.apply(GameplaySample(t=2, power_pill_active=True, **sample_feed),
        DijkstraDistances(player_to_ghost=[11], **dist_feed))

    metric.apply(GameplaySample(t=3, power_pill_active=True, **sample_feed),
        DijkstraDistances(player_to_ghost=[12], **dist_feed))

    assert metric.value == 0


def test_03_no_power_pill():
    sample_feed = {
        'player_pos': None,
        'ghost_pos': None,
        'player_dead': False,
        'victory': False
    }

    dist_feed = {
        'barrier_to_player': [20],
        'barrier_to_ghost': [19]
    }

    metric = A6_ChaseGhostsOrCollectDots()

    metric.apply(GameplaySample(t=0, power_pill_active=False, **sample_feed),
        DijkstraDistances(player_to_ghost=[10], **dist_feed))

    metric.apply(GameplaySample(t=1, power_pill_active=False, **sample_feed),
        DijkstraDistances(player_to_ghost=[9], **dist_feed))

    metric.apply(GameplaySample(t=2, power_pill_active=False, **sample_feed),
        DijkstraDistances(player_to_ghost=[9], **dist_feed))

    metric.apply(GameplaySample(t=3, power_pill_active=False, **sample_feed),
        DijkstraDistances(player_to_ghost=[8], **dist_feed))

    assert metric.value == 0
