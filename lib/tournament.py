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
        pass