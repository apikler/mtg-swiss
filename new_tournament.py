import argparse

from lib.tournament import Tournament

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Start a new tournament.')
    parser.add_argument('name', type=str, help='tournament name')
    parser.add_argument('players', type=str, nargs='+', help='player names, one arg per name')
    args = parser.parse_args()

    print(args.name)
    print(args.players)