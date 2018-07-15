import argparse
import csv

from lib.tournament import Tournament, MatchResult, PlayerMatchResult, print_pairings

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Record results')
    parser.add_argument('file', type=str, help='path to the tournament file')
    parser.add_argument('results', type=str, help='path to the results file')
    args = parser.parse_args()

    results = []
    with open(args.results) as results_csv:
        reader = csv.reader(results_csv)
        for row in reader:
            player_match_results = {}  # map from player name to PlayerMatchResult
            draws = 0
            for string in row:
                if ':' in string:
                    # This is a player score
                    player_name, wins = string.split(':')
                    wins = int(wins)
                    player_match_results[player_name] = PlayerMatchResult(player_name, wins)
                elif '-' in string:
                    # This is a drop
                    player_name = string[1:]
                    player_match_results[player_name].drop = True
                else:
                    # This is a number of draws.
                    draws = int(string)
            results.append(MatchResult(list(player_match_results.values()), draws=draws))

    tournament = Tournament.load(args.file)
    tournament.record_results(results)
    tournament.save()
    print_pairings(tournament.new_pairings())