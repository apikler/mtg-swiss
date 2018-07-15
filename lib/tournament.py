import random

from .player import Player

class Tournament(object):
    def __init__(self, name, player_names):
        self.name = name

        self.players = []
        for player_name in player_names:
            self.players.append(Player(player_name))

        # Number of the last completed round.
        self.round = 0

    def new_pairings(self):
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
            pairings.append((sorted_players[i], sorted_players[i+1]))

        if bye_player:
            pairings.append((bye_player,))

        return pairings
