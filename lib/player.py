class Player(object):
    def __init__(self, name):
        self.name = name
        self.match_points = 0
        self.game_points = 0
        self.had_bye = False

    def __repr__(self):
        return self.name