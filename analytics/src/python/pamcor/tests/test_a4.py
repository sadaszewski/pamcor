#
# Copyright (C) Stanislaw Adaszewski, 2018
#

from pamcor.common.behavior_metrics import A4_HuntEvenAfterPillFinished
from pamcor.common import GameplaySample, \
    DijkstraDistances


def test_01_hunt_after_pill_finished():
    metric = A4_HuntEvenAfterPillFinished()

    samples = []

    t = 0
    player_pos = (13, 23)
    ghost_pos = [ (14, 23) ]
    power_pill_active = True
    player_dead = False
    victory = False

    samples.append(GameplaySample(t, player_pos, ghost_pos, power_pill_active,
        player_dead, victory))

    t = 1
    power_pill_active = False

    samples.append(GameplaySample(t, player_pos, ghost_pos, power_pill_active,
        player_dead, victory))

    for i in range(1, 10):
        t = 1 + i / 10
        samples.append(GameplaySample(t, player_pos, ghost_pos, power_pill_active,
            player_dead, victory))

    player_to_ghost = [1]
    barrier_to_player = [20]
    barrier_to_ghost = [19]

    distances = DijkstraDistances(player_to_ghost,
        barrier_to_player,
        barrier_to_ghost)

    for sample in samples:
        metric.apply(sample, distances)

    assert metric.value == 10


def test_02_not_hunt_after_pill_finished():
    metric = A4_HuntEvenAfterPillFinished()

    samples = []

    t = 0
    player_pos = (13, 23)
    ghost_pos = [ (15, 23) ]
    power_pill_active = True
    player_dead = False
    victory = False

    samples.append(GameplaySample(t, player_pos, ghost_pos, power_pill_active,
        player_dead, victory))

    t = 1
    power_pill_active = False

    samples.append(GameplaySample(t, player_pos, ghost_pos, power_pill_active,
        player_dead, victory))

    for i in range(1, 10):
        t = 1 + i / 10
        samples.append(GameplaySample(t, player_pos, ghost_pos, power_pill_active,
            player_dead, victory))

    player_to_ghost = [2]
    barrier_to_player = [20]
    barrier_to_ghost = [19]

    distances = DijkstraDistances(player_to_ghost,
        barrier_to_player,
        barrier_to_ghost)

    for sample in samples:
        metric.apply(sample, distances)

    assert metric.value == 0


def test_03_no_pill():
    metric = A4_HuntEvenAfterPillFinished()

    samples = []

    t = 0
    player_pos = (13, 23)
    ghost_pos = [ (14, 23) ]
    power_pill_active = False
    player_dead = False
    victory = False

    samples.append(GameplaySample(t, player_pos, ghost_pos, power_pill_active,
        player_dead, victory))

    t = 1
    power_pill_active = False

    samples.append(GameplaySample(t, player_pos, ghost_pos, power_pill_active,
        player_dead, victory))

    for i in range(1, 10):
        t = 1 + i / 10
        samples.append(GameplaySample(t, player_pos, ghost_pos, power_pill_active,
            player_dead, victory))

    player_to_ghost = [1]
    barrier_to_player = [20]
    barrier_to_ghost = [19]

    distances = DijkstraDistances(player_to_ghost,
        barrier_to_player,
        barrier_to_ghost)

    for sample in samples:
        metric.apply(sample, distances)

    assert metric.value == 0


def test_04_too_late():
    metric = A4_HuntEvenAfterPillFinished()

    samples = []

    t = 0
    player_pos = (13, 23)
    ghost_pos = [ (14, 23) ]
    power_pill_active = True
    player_dead = False
    victory = False

    samples.append(GameplaySample(t, player_pos, ghost_pos, power_pill_active,
        player_dead, victory))

    t = 1
    power_pill_active = False

    samples.append(GameplaySample(t, player_pos, ghost_pos, power_pill_active,
        player_dead, victory))

    for i in range(1, 10):
        t = 4 + i / 10
        samples.append(GameplaySample(t, player_pos, ghost_pos, power_pill_active,
            player_dead, victory))

    player_to_ghost = [1]
    barrier_to_player = [20]
    barrier_to_ghost = [19]

    distances = DijkstraDistances(player_to_ghost,
        barrier_to_player,
        barrier_to_ghost)

    for sample in samples:
        metric.apply(sample, distances)

    assert metric.value == 1
