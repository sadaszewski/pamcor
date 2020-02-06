#
# Copyright (C) Stanislaw Adaszewski, 2018
#

from argparse import ArgumentParser
import json
import numpy as np
import os
from pamcor.common import parse_log


def create_parser():
    parser = ArgumentParser()
    parser.add_argument('path_to_pamcor_export', type=str)
    parser.add_argument('--exclude-names', '-x', type=str, nargs='+', default=[])
    parser.add_argument('--output-directory', '-o', type=str, default='./json_logs')
    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()

    print('Loading data ...')
    with open(args.path_to_pamcor_export, 'r') as f:
        data = json.loads(f.read())

    print('Parsing logs ...')
    uids = []
    names = []
    for (uid, logs) in data['logs'].items():
        player = data['player'][uid]
        if player['nickname'] in args.exclude_names:
            continue
        uids.append(uid)
        names.append(player['nickname'])

    idx = np.argsort(names)
    uids = np.array(uids)[idx]

    for i in range(len(uids)):
        uid = uids[i]
        print('Parsing log for:', data['player'][uid]['nickname'])

        for (date, text) in data['logs'][uid].items():
            print('Date:', date)

            log = parse_log(text)

            if log is None:
                print('Skipping ...')
                continue

            path = os.path.join(args.output_directory, names[i])
            try:
                os.makedirs(path)
            except FileExistsError:
                pass

            path = os.path.join(path, date + '.json')
            with open(path, 'w') as f:
                output = list(map(lambda a: a.dict(), log))
                f.write(json.dumps(output, sort_keys=True,
                    indent=4, separators=(',', ': ')))


if __name__ == '__main__':
    main()
