#
# Copyright (C) Stanislaw Adaszewski, 2018
#


from .log_entry import *

def parse_log(text):
    text = text.strip('\u0000')
    res = []

    entry_classes = [
        StartingGame,
        BackgroundColor,
        Ch1Color,
        Ch2Color,
        BiggerConfig,
        ShiftConfig,
        ScreenSizeConfig,
        DifficultyConfig,
        RedBlueFlipConfig,
        ContrastConfig,
        WeakerConfig,
        CreatingMaze,
        PlacedGhost,
        PlacedPlayer,
        GameStarted,
        AutomaticContrastDecrase,
        ForcedCalibrationProcedure,
        TouchEventBegan,
        PlayerSwiped,
        ApplicationForeground,
        ApplicationBackground
    ]

    magic = re.compile('[0-9]\\.[0-9]{6} ')
    pos = 0
    line_starts = []
    timestamps = []

    while True:
        match = magic.search(text, pos)

        if match is None:
            line_starts.append(len(text))
            break # return None

        line_starts.append(match.start(0))
        timestamps.append(float(match.group(0)))
        pos = match.end(0)

        msg = text[pos:pos+12]

        if msg == 'Game started':
            break

    # print(line_starts)

    for i in range(len(line_starts) - 1):
        for cls in entry_classes:
            match = cls.search(text, line_starts[i] + 9, line_starts[i + 1])
            if match is None:
                continue
            entry = cls.create(match, timestamps[i])
            entry.parse()
            res.append(entry)
            break

        if match is None:
            raise ValueError('Unrecognized log entry: %s' % text[line_starts[i]+9:line_starts[i+1]])

    entry_classes = [
        GameStarted,
        GhostMoves,
        PlayerMoves,
        PlayerAtePill,
        TouchEventBegan,
        PlayerSwiped,
        PlayerKilled,
        GameOver,
        NextLevel,
        PlayerAtePowerPill,
        GainedBonus,
        PowerPillEnded,
        ApplicationQuit,
        ApplicationForeground,
        ApplicationBackground,
        PlayerWarped,
        GhostWarped
    ]

    pos = line_starts[-1]
    magic = re.compile('([0-9]+)\\.[0-9]{6} ')

    while pos < len(text):
        match = magic.search(text, pos)
        if match is None or match.start(0) != pos:
            print('Timestamp expected but not found')
            break

        magic_match = match
        game_time = float(magic_match.group(0))
        pos += len(match.group(0))

        ok = False
        for cls in entry_classes:
            match = cls.search(text, pos)
            if match is not None and match.start(0) == pos:
                if cls.rx.groups > 0:
                    last_grp = match.group(cls.rx.groups)

                    if last_grp[0] != '-' and len(last_grp) > 1 and \
                        ord(last_grp[-1]) >= ord('0') and ord(last_grp[-1]) <= ord('9') and \
                        match.end(0) < len(text):

                        if cls in (PlayerKilled, PlayerWarped, GhostWarped):
                            # print('here')
                            match = cls.search(text, pos, match.end(0) - len(magic_match.group(0)) + 1)
                            next_pos = pos + len(match.group(0))
                            ahead = magic.search(text, next_pos)
                            if next_pos < len(text) and \
                                (ahead is None or ahead.start(0) != next_pos or \
                                float(ahead.group(0)) < game_time):
                                print('!!!!!! oops, we probably ate a digit too much')
                                match = cls.search(text, pos, match.end(0) - 1)

                        elif cls in (PlayerAtePill, PlayerAtePowerPill, GainedBonus):
                            pass

                        else:
                            # print(match, magic_match)
                            match = cls.search(text, pos, match.end(0) - magic_match.group(0).index('.'))
                            next_pos = pos + len(match.group(0))
                            ahead = magic.search(text, next_pos)
                            if next_pos < len(text) and \
                                (ahead is None or ahead.start(0) != next_pos or \
                                float(ahead.group(0)) < game_time):
                                print('oops, we probably ate a digit too much')
                                # print(game_time, match)
                                match = cls.search(text, pos, match.end(0) - 1)
                                # print(match)

                pos += len(match.group(0))
                ok = True
                entry = cls.create(match, game_time)
                entry.parse()
                res.append(entry)
                break

        if not ok:
            raise ValueError('Unrecognized log entry encountered at pos: %d ... %s ...' % (pos, text[pos:pos+50]))

    return res
