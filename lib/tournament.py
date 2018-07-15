import os
import pickle
import random

class TournamentException(Exception):
    pass

def print_pairings(pairings):
    for pair in pairings:
        if len(pair) == 1:
            print('%s (BYE)' % pair[0])
        else:
            print('%s, %s' % (pair[0], pair[1]))

class Player(object):
    def __init__(self, name):
        self.name = name
        self.match_points = 0
        self.game_points = 0
        self.had_bye = False

        # Set of player names
        self.already_played = set()

    def __repr__(self):
        return self.name


class PlayerMatchResult(object):
    def __init__(self, name, wins, drop=False):
        self.name = name
        self.wins = wins
        self.drop = drop


class MatchResult(object):
    def __init__(self, player_results, draws=0):
        if len(player_results) not in (1, 2):
            raise TournamentException('Need exactly 1 or 2 player results; %d provided' % len(player_results))
        self.player_results = player_results
        self.draws = draws

    def winner(self):
        if len(self.player_results) == 1:
            return self.player_results[0].name
        else:
            if self.player_results[0].wins > self.player_results[1].wins:
                return self.player_results[0].name
            elif self.player_results[1].wins > self.player_results[0].wins:
                return self.player_results[1].name


class Tournament(object):
    def __init__(self, name, player_names):
        self.name = name
        self.dir = None

        self.all_players = {}
        self.players = []
        for player_name in player_names:
            player = Player(player_name)
            self.players.append(player)
            self.all_players[player_name] = player

        # Number of the last completed round.
        self.round = 0

    @classmethod
    def load(cls, path):
        with open(path, 'rb') as f:
            tournament = pickle.load(f)
            tournament.dir = os.path.dirname(path)
            return tournament

    def new_pairings(self):
        pairings = self.__generate_pairings()
        while not self.__validate_pairings(pairings):
            pairings = self.__generate_pairings()
        return pairings

    def record_results(self, results):
        self.__validate_results(results)

        for result in results:
            players = []
            for player_result in result.player_results:
                player = self.all_players[player_result.name]
                player.game_points += 3*player_result.wins + result.draws
                players.append(player)

            winner = result.winner()
            if winner:
                self.all_players[winner].match_points += 3
            else:
                for player in players:
                    player.match_points += 1

            if len(players) == 1:
                players[0].had_bye = True
            else:
                players[0].already_played.add(players[1].name)
                players[1].already_played.add(players[0].name)

        self.round += 1

    def save(self, dir=None):
        save_dir = dir or self.dir
        with open(os.path.join(save_dir, '%s_round%d.mtg' % (self.name, self.round)), 'wb') as f:
            pickle.dump(self, f)

    def __generate_pairings(self):
        sorted_players = self.players[:]
        random.shuffle(sorted_players)
        sorted_players.sort(key=lambda player: player.match_points)

        bye_player = None
        if len(sorted_players) % 2 != 0:
            for i, player in enumerate(sorted_players):
                if not player.had_bye:
                    break
            bye_player = sorted_players.pop(i)

        sorted_players.reverse()
        pairings = []
        for i in range(0, len(sorted_players), 2):
            pairings.append((sorted_players[i].name, sorted_players[i+1].name))

        if bye_player:
            pairings.append((bye_player.name,))

        return pairings

    def __validate_pairings(self, pairings):
        for pair in pairings:
            if len(pair) == 1:
                player = self.all_players[pair[0]]
                if player.had_bye:
                    return False
            else:
                player1 = self.all_players[pair[0]]
                if pair[1] in player1.already_played:
                    return False
        return True

    def __validate_results(self, results):
        player_names = self.__current_player_names()

        for result in results:
            for player_result in result.player_results:
                if player_result.name not in player_names:
                    raise TournamentException('Player not in tournament or duplicate result: %s' % player_result.name)
                player_names.remove(player_result.name)

        if player_names:
            raise TournamentException('Results not entered for the following players: %s' % list(player_names))

    def __current_player_names(self):
        names = set()
        for player in self.players:
            names.add(player.name)
        return names
