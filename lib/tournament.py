import copy
import os
import pickle
import random

class TournamentError(Exception):
    pass

def print_pairings(pairings):
    for pair in pairings:
        if len(pair) == 1:
            print('%s (BYE)' % pair[0])
        else:
            print('%s, %s' % (pair[0], pair[1]))

def print_rankings_csv(rankings):
    print('rank,name,match points,opp match win %,game win %,opp game win %')
    for i, player in enumerate(rankings):
        print(','.join([
            str(i+1),
            player.name, 
            str(player.match_points), 
            '%.2f' % player.opp_match_win_percent, 
            '%.2f' % player.game_win_percent, 
            '%.2f' % player.opp_game_win_percent]))

class Player(object):
    def __init__(self, name):
        self.name = name
        self.match_points = 0
        self.game_points = 0
        self.games_played = 0
        self.had_bye = False

        # Set of player names
        self.already_played = set()

    def __repr__(self):
        return self.name

    def rounds_played(self):
        count = len(self.already_played)
        if self.had_bye:
            count += 1
        return count


class PlayerMatchResult(object):
    def __init__(self, name, wins, drop=False):
        self.name = name
        self.wins = wins
        self.drop = drop


class MatchResult(object):
    def __init__(self, player_results, draws=0):
        if len(player_results) not in (1, 2):
            raise TournamentError('Need exactly 1 or 2 player results; %d provided' % len(player_results))
        self.player_results = player_results
        self.draws = draws

    def games_played(self):
        count = self.draws
        for result in self.player_results:
            count += result.wins
        return count

    def unplayed(self):
        return len(self.player_results) == 2 and self.player_results[0].wins == 0 and self.player_results[1].wins == 0

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
                player.games_played += result.games_played()
                players.append(player)

            if not result.unplayed():
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

            for player_result in result.player_results:
                if player_result.drop:
                    for i, player in enumerate(self.players):
                        if player.name == player_result.name:
                            self.players.pop(i)

        for player in self.all_players.values():
            try:
                player.match_win_percent = max(player.match_points / (3 * player.rounds_played()), 0.33)
            except ZeroDivisionError:
                player.match_win_percent = 0.33

            try:
                player.game_win_percent = max(player.game_points / (3 * player.games_played), 0.33)
            except ZeroDivisionError:
                player.game_win_percent = 0.33
        for player in self.all_players.values():
            match_total = 0
            game_total = 0
            for opponent_name in player.already_played:
                match_total += self.all_players[opponent_name].match_win_percent
                game_total += self.all_players[opponent_name].game_win_percent
            try:
                player.opp_match_win_percent = match_total / len(player.already_played)
            except ZeroDivisionError:
                player.opp_match_win_percent = 0.33
            try:
                player.opp_game_win_percent = game_total / len(player.already_played)
            except ZeroDivisionError:
                player.opp_game_win_percent = 0.33

        self.round += 1

    def save(self, dir=None):
        save_dir = dir or self.dir
        with open(os.path.join(save_dir, '%s_round%d.mtg' % (self.name, self.round)), 'wb') as f:
            pickle.dump(self, f)

    def rankings(self):
        players = copy.deepcopy(self.players)
        players.sort(
            reverse=True,
            key=lambda player: (
                player.match_points, 
                player.opp_match_win_percent, 
                player.game_win_percent, 
                player.opp_game_win_percent))
        return players

    def __generate_pairings(self):
        sorted_players = copy.deepcopy(self.players[:])

        # Fix the scores so everyone has a multiple of 3. Anyone who doesn't gets
        # rounded up or down randomly.
        for player in sorted_players:
            remainder = player.match_points % 3
            if remainder != 0:
                player.match_points -= remainder
                if random.randint(0, 1):
                    player.match_points += 3

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
                    raise TournamentError('Player not in tournament or duplicate result: %s' % player_result.name)
                player_names.remove(player_result.name)

        if player_names:
            raise TournamentError('Results not entered for the following players: %s' % list(player_names))

    def __current_player_names(self):
        names = set()
        for player in self.players:
            names.add(player.name)
        return names
