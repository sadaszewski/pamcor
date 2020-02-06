#
# Copyright (C) Stanislaw Adaszewski, 2018
#

import re
import json


class LogEntry(object):
    def parse(self):
        m, rx, types = self.m, self.rx, self.types
        groupindex = [(k, v) for (k, v) in rx.groupindex.items()]
        groupindex = sorted(groupindex, key=lambda a: a[1])
        groupindex = { groupindex[i][0]: i for i in range(len(groupindex)) }
        for (k, v) in m.groupdict().items():
            # print('k:', k)
            idx = groupindex[k]
            type_ = types[idx]
            setattr(self, k, type_(v))

    def dict(self):
        m, rx, types = self.m, self.rx, self.types
        groupindex = [(k, v) for (k, v) in rx.groupindex.items()]
        groupindex = sorted(groupindex, key=lambda a: a[1])
        groupindex = { groupindex[i][0]: i for i in range(len(groupindex)) }
        res = {
            'entry': self.__class__.__name__,
            'game_time': self.game_time
        }
        for (k, v) in m.groupdict().items():
            idx = groupindex[k]
            type_ = types[idx]
            res[k] = type_(v)
        return res

    @classmethod
    def match(cls, line):
        return cls.rx.match(line)

    @classmethod
    def search(cls, text, pos=0, endpos=None):
        return cls.rx.search(text, pos, endpos) \
            if endpos is not None \
            else cls.rx.search(text, pos)

    @classmethod
    def create(cls, m, game_time=0):
        res = cls()
        res.m = m
        res.game_time = game_time
        return res

    def json(self):
        return json.dumps(self.dict())

    @staticmethod
    def from_dict(data):
        cls = _entry_class_dict[data['entry']]
        entry = cls()
        for g in cls.rx.groupindex.keys():
            setattr(entry, g, data[g])
        setattr(entry, 'game_time', data['game_time'])
        return entry


class StartingGame(LogEntry):
    rx = re.compile('Starting game, level: (?P<level>[0-9]+), score: (?P<score>[0-9]+), hiscore: (?P<hiscore>[0-9]+)')
    types = (int, int, int)


class BackgroundColor(LogEntry):
    rx = re.compile('Background: (?P<red>[0-9]+), (?P<green>[0-9]+), (?P<blue>[0-9]+), (?P<alpha>[0-9]+(\\.[0-9]+)?)')
    types = (int, int, int, float)


class Ch1Color(LogEntry):
    rx = re.compile('Ch 1: (?P<red>[0-9]+), (?P<green>[0-9]+), (?P<blue>[0-9]+), (?P<alpha>[0-9]+(\\.[0-9]+)?)')
    types = (int, int, int, float)


class Ch2Color(LogEntry):
    rx = re.compile('Ch 2: (?P<red>[0-9]+), (?P<green>[0-9]+), (?P<blue>[0-9]+), (?P<alpha>[0-9]+(\\.[0-9]+)?)')
    types = (int, int, int, float)


class BiggerConfig(LogEntry):
    rx = re.compile('Bigger: (?P<bigger>True|False)')
    types = (lambda a: a == 'True',)


class ShiftConfig(LogEntry):
    rx = re.compile('Shift: (?P<shift>[0-9]+(\\.[0-9]+)?)')
    types = (float,)


class ScreenSizeConfig(LogEntry):
    rx = re.compile('Screen size: (?P<width>[0-9]+), (?P<height>[0-9]+)')
    types = (int, int)


class DifficultyConfig(LogEntry):
    rx = re.compile('Difficulty: (?P<difficulty>[0-9]+)')
    types = (int,)


class RedBlueFlipConfig(LogEntry):
    rx = re.compile('Red/Blue Flip: (?P<red_blue_flip>[0-9]+)')
    types = (int,)


class ContrastConfig(LogEntry):
    rx = re.compile('Contrast: (?P<contrast>[0-9]+(\\.[0-9]+)?)')
    types = (float,)


class WeakerConfig(LogEntry):
    rx = re.compile('Weaker: (?P<weaker>0|1)')
    types = (int,)


class CreatingMaze(LogEntry):
    rx = re.compile('Creating maze, level: (?P<level>[0-9]+)')
    types = (int,)


class PlacedGhost(LogEntry):
    rx = re.compile('Placed ghost: (?P<ghost_index>[0-9]+) at x: (?P<x>[0-9]+), y: (?P<y>[0-9]+), delay: (?P<delay>[0-9]+(\\.[0-9]+)?)')
    types = (int, int, int, float)


class PlacedPlayer(LogEntry):
    rx = re.compile('Placed player at x: (?P<x>[0-9]+), y: (?P<y>[0-9]+), delay: (?P<delay>[0-9]+(\\.[0-9]+)?)')
    types = (int, int, float)


class GameStarted(LogEntry):
    rx = re.compile('Game started')
    types = ()


class AutomaticContrastDecrase(LogEntry):
    rx = re.compile('Automatic contrast decreased to: (?P<contrast>-?[0-9]+(\\.[0-9]+)?)')
    types = (float,)


class ForcedCalibrationProcedure(LogEntry):
    rx = re.compile('No wins, more than five fails, starting calibration procedure from contrast: (?P<contrast>[0-9]+(\\.[0-9]+)?)')
    types = (float,)


class TouchEventBegan(LogEntry):
    rx = re.compile('Touch event began')
    types = ()


class PlayerSwiped(LogEntry):
    rx = re.compile('Player swiped: (?P<direction>left|right|down|up)')
    types = (str,)


class ApplicationForeground(LogEntry):
    rx = re.compile('Application moving to foreground, UTC date/time is: [0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}\\.[0-9]{7}Z')
    types = ()


class ApplicationBackground(LogEntry):
    rx = re.compile('Application moving to background')
    types = ()


class GhostMoves(LogEntry):
    rx = re.compile('Ghost: (?P<ghost_index>[0-9]+) moves from x: (?P<x>[0-9]+), y: (?P<y>[0-9]+), dx: (?P<dx>0|1|-1), dy: (?P<dy>0|1|-1)')
    types = (int, int, int, int, int)


class PlayerMoves(LogEntry):
    rx = re.compile('Player moving from x: (?P<x>[0-9]+), y: (?P<y>[0-9]+), dx: (?P<dx>0|1|-1), dy: (?P<dy>0|1|-1)')
    types = (int, int, int, int)


class PlayerAtePill(LogEntry):
    rx = re.compile('Player ate a pill, score increase: (?P<score_increase>10|20|30)')
    types = (int,)


class PlayerKilled(LogEntry):
    rx = re.compile('Player was killed by ghost: (?P<ghost_index>[0-9]+) at x: (?P<x>[0-9]+(\\.[0-9]+)?), y: (?P<y>[0-9]+([\\.0-9]+)?)')
    types = (int, float, float)


class GameOver(LogEntry):
    rx = re.compile('Game over, score: (?P<score>[0-9]+), hiscore: (?P<hiscore>[0-9]+)')
    types = (int, int)


class NextLevel(LogEntry):
    rx = re.compile('Player passed to next level: (?P<level>[0-9]+), score: (?P<score>[0-9]+), hiscore: (?P<hiscore>[0-9]+)')
    types = (int, int, int)


class PlayerAtePowerPill(LogEntry):
    rx = re.compile('Player ate a power pill, bonus: (?P<bonus>50)')
    types = (int,)


class GainedBonus(LogEntry):
    rx = re.compile('Gained bonus: (?P<bonus>50|100|200|400|800|1600|3200|6400|12800|25600|75|150|300|600|1200|2400|4800|9600|19200)')
    types = (int,)


class PowerPillEnded(LogEntry):
    rx = re.compile('Power pill effect ended')
    types = ()


class ApplicationQuit(LogEntry):
    rx = re.compile('Application quit')
    types = ()


class PlayerWarped(LogEntry):
    rx = re.compile('Player warped to x: (?P<x>[0-9]+([\\.0-9]+)?)')
    types = (float,)


class GhostWarped(LogEntry):
    rx = re.compile('Ghost: (?P<ghost_index>[0-9]+) warped to x: (?P<x>[0-9]+([\\.0-9]+)?)')
    types = (int, float)


_entry_classes = [StartingGame, BackgroundColor, Ch1Color, Ch2Color, BiggerConfig,
    ShiftConfig, ScreenSizeConfig, DifficultyConfig, RedBlueFlipConfig,
    ContrastConfig, WeakerConfig, CreatingMaze, PlacedGhost, PlacedPlayer, GameStarted,
    AutomaticContrastDecrase, ForcedCalibrationProcedure, TouchEventBegan,
    PlayerSwiped, ApplicationForeground, ApplicationBackground,
    GhostMoves, PlayerMoves, PlayerAtePill, PlayerKilled, GameOver,
    NextLevel, PlayerAtePowerPill, GainedBonus, PowerPillEnded,
    ApplicationQuit, PlayerWarped, GhostWarped]

_entry_class_dict = { cls.__name__: cls for cls in _entry_classes }
