#
# Copyright (C) Stanislaw Adaszewski, 2018
#

from .behavior_metrics import *

class BehaviorAnalysis(object):
    metrics = [
        A1_HuntCloseToGhostHouse,
        A4_HuntEvenAfterPillFinished,
        A6_ChaseGhostsOrCollectDots,
        C1a_TimesTrappedByGhosts_fast,
        C2a_AverageDistanceToGhosts,
        C2b_AverageDistanceDuringHunt,
        C3_CloseCalls,
        C4_CaughtAfterHunt
    ]

    def __init__(self):
        self.metrics = list(map(lambda cls: cls(), self.metrics))

    def apply(self, sample, **kwargs):
        for m in self.metrics:
            m.apply(sample, **kwargs)
