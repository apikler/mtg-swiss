import argparse

from lib.tournament import Tournament, print_pairings

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Start a new tournament.')
    parser.add_argument('name', type=str, help='tournament name')
    parser.add_argument('players', type=str, nargs='+', help='player names, one arg per name')
    parser.add_argument('--save_to', type=str, default='.')
    args = parser.parse_args()

    tournament = Tournament(args.name, args.players)
    tournament.save(args.save_to)
    print_pairings(tournament.new_pairings())