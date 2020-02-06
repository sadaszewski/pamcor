from argparse import ArgumentParser
from .interactive import main as interactive_main
from pamcor.learning import main as learning_main
from pamcor.common import Maze


def create_parser():
    parser = ArgumentParser()
    parser.add_argument('--maze', type=int,
        choices=[0, 1, 2, 3], default=0)
    parser.add_argument('--learning', action='store_true')
    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()
    maze = Maze.from_file(f'data/maze/maze{args.maze}.txt')
    feed = {
        'maze': maze,
        'args': args
    }
    if args.learning:
        learning_main(**feed)
    else:
        interactive_main(**feed)
