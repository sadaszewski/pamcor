#
# Copyright (C) Stanislaw Adaszewski, 2018
#


import numpy as np
from .util import SlidingTimeWindow


def _manhattan_distance(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


class BehaviorMetric(object):
    def apply(self, sample, **kwargs):
        raise NotImplementedError

    def __repr__(self):
        return '%s: %s' % (self.__class__.__name__, repr(self.value))


class A1_HuntCloseToGhostHouse(BehaviorMetric):
    def __init__(self):
        self.value = 0

    def apply(self, sample, distances, **kwargs):
        if sample.power_pill_active and \
            distances.barrier_to_player < 5 and \
            min(distances.barrier_to_ghost) < 3:
            self.value += 1


class A4_HuntEvenAfterPillFinished(BehaviorMetric):
    def __init__(self):
        self.value = 0
        self.power_pill_active = None
        self.power_up_timestamp = None
        self.power_down_timestamp = None
        self.seconds_after_power_down = 2

    def apply(self, sample, distances, **kwargs):
        if self.power_pill_active is None:
            self.power_pill_active = sample.power_pill_active
        elif self.power_pill_active != sample.power_pill_active:
            self.power_pill_active = sample.power_pill_active
            if sample.power_pill_active:
                self.power_up_timestamp = sample.t
            else:
                self.power_down_timestamp = sample.t

        if self.power_down_timestamp is not None and \
            sample.t - self.power_down_timestamp < \
            self.seconds_after_power_down and \
            min(distances.player_to_ghost) <= 1:

            self.value += 1

            # while(PacAtkBool@State(t-20)){ if(
            # dist(PacXY, Gst{1,2}XY) == 1 )then
            # Output++ }


class A6_ChaseGhostsOrCollectDots(BehaviorMetric):
    def __init__(self):
        self.value = 0
        self.player_to_ghost = None

    def apply(self, sample, distances, **kwargs):
        # while(PacAtkBool){ if( dist(PacXY,
        # Gst{1,2}XY):decrease) then Output++
        if sample.power_pill_active and \
            self.player_to_ghost is not None and \
            np.any((distances.player_to_ghost - self.player_to_ghost) < 0):
            self.value += 1
        self.player_to_ghost = np.array(distances.player_to_ghost)


class C1a_TimesTrappedByGhosts(BehaviorMetric):
    def __init__(self):
        self.value = 0
        self.cached_key = None
        self.cached_longest = None

    def apply(self, sample, maze, **kwargs):
        max_dist = 20
        player_pos = tuple(map(round, sample.player_pos[:2]))
        ghost_pos = tuple(map(lambda a: tuple(map(round, a[:2])), sample.ghost_pos))
        key = (player_pos, ghost_pos)
        longest = maze.trapped_by_ghosts(sample.player_pos,
            sample.ghost_pos, max_dist=max_dist) \
            if key != self.cached_key \
            else self.cached_longest
        if longest < max_dist:
            self.value += 1
        self.cached_key = key
        self.cached_longest = longest


class C1a_TimesTrappedByGhosts_fast(BehaviorMetric):
    def __init__(self):
        self.value = 0

    def apply(self, sample, maze, accessible, **kwargs):
        x, y = map(round, sample.player_pos[:2])

        def touching_a_ghost(x, y):
            for gp in sample.ghost_pos:
                if (gp[0] - x) ** 2 + (gp[1] - y) ** 2 < .25:
                    return True
            return False

        FREE = 0
        BLOCKED = 1
        GHOST = 2

        left = FREE
        right = FREE
        up = FREE
        down = FREE

        if x + 1 >= maze.width() or not accessible[y, x + 1]:
            right = BLOCKED
        else:
            for x_1 in range(x, maze.width()):
                if not accessible[y, x_1]: break
                if touching_a_ghost(x_1, y):
                    right = GHOST
                    break

        if x - 1 < 0 or not accessible[y, x - 1]:
            left = BLOCKED
        else:
            for x_1 in range(x, 0, -1):
                if not accessible[y, x_1]: break
                if touching_a_ghost(x_1, y):
                    left = GHOST
                    break

        if y - 1 < 0 or not accessible[y - 1, x]:
            up = BLOCKED
        else:
            for y_1 in range(y, 0, -1):
                if not accessible[y_1, x]: break
                if touching_a_ghost(x, y_1):
                    up = GHOST
                    break

        if y + 1 >= maze.height() or not accessible[y + 1, x]:
            down = BLOCKED
        else:
            for y_1 in range(y, maze.height()):
                if not accessible[y_1, x]: break
                if touching_a_ghost(x, y_1):
                    down = GHOST
                    break

        if left != FREE and right != FREE and \
            up != FREE and down != FREE:
            self.value += 1

        # self.cached_key = key
        # self.cached_longest = longest


class C1b_TimesTrappedAndKilledByGhosts(BehaviorMetric):
    def __init__(self):
        self.value = 0

    def apply(self, sample, distances, **kwargs):
        # if( (C1.a_Times Trapped By Ghosts) &
        # Lives@State(t+10):decrease )
        # then Output++
        pass


class C2a_AverageDistanceToGhosts(BehaviorMetric):
    def __init__(self):
        self.sum = 0
        self.count = 0
        self.value = None

    def apply(self, sample, **kwargs):
        if sample.power_pill_active:
            return

        n_ghosts = len(sample.ghost_pos)
        for i in range(n_ghosts):
            self.sum += _manhattan_distance(sample.player_pos,
                sample.ghost_pos[i]) / n_ghosts
        self.count += 1
        self.value = self.sum / self.count


class C2b_AverageDistanceDuringHunt(BehaviorMetric):
    def __init__(self):
        self.sum = 0
        self.count = 0
        self.value = None

    def apply(self, sample, **kwargs):
        if not sample.power_pill_active:
            return

        n_ghosts = len(sample.ghost_pos)
        for i in range(n_ghosts):
            self.sum += _manhattan_distance(sample.player_pos,
                sample.ghost_pos[i]) / n_ghosts
        self.count += 1
        self.value = self.sum / self.count


class C3_CloseCalls(BehaviorMetric):
    # if( dist(PacXY, Gst{1,2}XY)@State(t-
    # 5) == 1 & Lives@State(t-5) == Lives)
    # then Output++

    def __init__(self):
        self.value = 0
        self.time_window = SlidingTimeWindow(6)

    def apply(self, sample, distances, **kwargs):
        close_to_ghost = (min(distances.player_to_ghost) <= 1)
        dead = sample.player_dead
        power_pill_active = sample.power_pill_active
        old = self.time_window.look_in_the_past(sample.t - 5)
        # print('t:', sample.t, 'old:', old, 'dead:', dead,
            # 'time_window:', self.time_window.samples)
        if old is not None and old[0] and not old[1] and not dead:
            self.value += 1
        self.time_window.append(sample.t, (close_to_ghost, power_pill_active))


class C4_CaughtAfterHunt(BehaviorMetric):
    # if( PacAtkBool@State(t-16) &
    # !PacAtkBool(t-15) & (Lives(t-15) >
    # Lives@State(t))) then Output++

    def __init__(self):
        self.value = 0
        self.time_window = SlidingTimeWindow(31)

    def apply(self, sample, **kwargs):
        power_pill_active = sample.power_pill_active
        player_dead = sample.player_dead
        then = self.time_window.look_in_the_past(sample.t - 16)
        later = self.time_window.look_in_the_past(sample.t - 15)
        now = (power_pill_active, player_dead)
        if then is not None and later is not None and \
            then[0] and not later[0] and now[1]:
            self.value += 1
        self.time_window.append(sample.t, now)


class C5_MovesWithNoPointsScored(BehaviorMetric):
    pass


class C7_KilledAtGhostHouse(BehaviorMetric):
    pass


class CherryOnScreenTime(BehaviorMetric):
    pass


class D2_PacmanVacillating(BehaviorMetric):
    pass


class P1_WaitsNearPillToLureGhosts(BehaviorMetric):
    pass


class P1a_CountMovesWhileWaitingForGhosts(BehaviorMetric):
    pass


class P1c_NumberOfGhostsEatenAfterLure(BehaviorMetric):
    pass


class P1d_CaughtBeforeEatingPill(BehaviorMetric):
    pass


class P4a_AverageSpeedHunting1stGhost(BehaviorMetric):
    pass


class P4b_AverageSpeedHunting2ndGhost(BehaviorMetric):
    pass


class PointsMax(BehaviorMetric):
    pass


class S2a_LivesGained(BehaviorMetric):
    pass


class S2b_LivesLost(BehaviorMetric):
    pass


class S4_TeleportUse(BehaviorMetric):
    pass
