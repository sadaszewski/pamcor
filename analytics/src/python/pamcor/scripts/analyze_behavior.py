#
# Copyright (C) Stanislaw Adaszewski, 2018
#

from argparse import ArgumentParser
from glob import glob
import os
import json
from pamcor.common.log_entry import *
from pamcor.common import BehaviorAnalysis, \
    Entity, \
    GameplaySample, \
    Maze, \
    DijkstraDistances, \
    DijkstraPrecompute
import sys
import csv


def create_parser():
    parser = ArgumentParser()
    parser.add_argument('--json-logs', '-l', type=str, default='./json_logs')
    parser.add_argument('--data-directory', '-d', type=str, default='./data')
    parser.add_argument('--output-file', '-o', type=str, default='behavior.csv')
    return parser


def distance(a, b):
    return ((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2) ** 0.5


def process_log(fnam, log, args, callback=None):
    player = None
    n_ghosts = 3
    ghosts = [None] * n_ghosts
    ghost_dead = [False] * n_ghosts
    power_pill_active = False
    player_dead = False
    victory = False
    n_levels = 4
    maze = None
    accessible = None
    # precompute = None

    t_0 = None
    for i in range(len(log)):
        entry = log[i]
        if isinstance(entry, StartingGame):
            level_nr = entry.level % n_levels
            maze = Maze.from_file(os.path.join(args.data_directory,
                'maze', 'maze%d.txt' % level_nr))
            accessible = maze.accessible_mask()
            maze.dijkstra_precompute()
            # precompute = DijkstraPrecompute(maze)
            # precompute.run()
        elif isinstance(entry, PlacedGhost):
            ghosts[entry.ghost_index] = Entity(entry.x, entry.y, entry.delay)
        elif isinstance(entry, PlacedPlayer):
            player = Entity(entry.x, entry.y, entry.delay)
        elif isinstance(log[i], GameStarted):
            t_0 = log[i].game_time
            break

    if t_0 is None:
        return None

    i += 1
    t = t_0
    player_samples = []
    ghost_samples = []
    t_samples = []

    while i < len(log) and not player_dead and not victory:
        player_pos = player.sample_pos(t)
        ghost_pos = list(map(lambda a: a.sample_pos(t), ghosts))

        for k, g_pos in enumerate(ghost_pos):
            if distance(g_pos, player_pos) < .5:
                if power_pill_active and \
                    not ghost_dead[k]:
                    ghost_dead[k] = True
                    ghost_pos[k] += ('killed',)
                elif not power_pill_active and \
                    not player_dead:
                    player_pos += ('killed',)
                    player_dead = True

        if player_dead:
            player_pos += ('dead',)

        while i < len(log) and t >= log[i].game_time and not player_dead and not victory:
            entry = log[i]
            if isinstance(entry, GhostMoves):
                ghosts[entry.ghost_index].move(t, entry.x, entry.y, entry.dx, entry.dy)
                ghost_dead[k] = False
            elif isinstance(entry, PlayerMoves):
                player.move(t, entry.x, entry.y, entry.dx, entry.dy)
            elif isinstance(entry, PlayerAtePill):
                player_pos += ('pill',)
            elif isinstance(entry, PlayerAtePowerPill):
                power_pill_active = True
                player_pos += ('power_pill',)
            elif isinstance(entry, PowerPillEnded):
                power_pill_active = False
                player_pos += ('power_pill_end',)
            elif isinstance(entry, NextLevel):
                victory = True
                player_pos += ('victory',)
            elif isinstance(entry, GameOver):
                pass
            i += 1

        sample = GameplaySample(t, player_pos, ghost_pos, power_pill_active,
            player_dead, victory)
        distances = DijkstraDistances.from_maze_and_sample(maze, sample)
        if callback is not None:
            callback(sample=sample, distances=distances,
                maze=maze, accessible=accessible)

        player_samples.append(player_pos)
        ghost_samples.append(ghost_pos)
        t_samples.append(t)

        t += 0.01

    # print('player_samples:', player_samples)
    # print('ghost_samples:', ghost_samples)
    # print('t_samples:', t_samples)
    # sys.exit(0)


def main():
    parser = create_parser()
    args = parser.parse_args()
    fnames = glob(os.path.join(args.json_logs, '*', '*.json'))

    writer = csv.writer(open(args.output_file, 'w'))
    analysis = BehaviorAnalysis()
    writer.writerow(['Subject', 'Date'] + list(map(lambda a: a.__class__.__name__, analysis.metrics)))

    for fnam in fnames:
        print('Processing:', fnam, '...')
        data = open(fnam, 'r').read()
        if len(data) == 0:
            print('Skipping empty:', fnam, '...')
            continue
        data = json.loads(data)
        log = list(map(LogEntry.from_dict, data))
        analysis = BehaviorAnalysis()
        process_log(fnam, log, args, analysis.apply)
        # print(analysis.metrics)
        (path, date) = os.path.split(fnam)
        (patj, subj) = os.path.split(path)
        (date, ext) = os.path.splitext(date)
        writer.writerow([subj, date] + list(map(lambda a: a.value, analysis.metrics)))


if __name__ == '__main__':
    main()
