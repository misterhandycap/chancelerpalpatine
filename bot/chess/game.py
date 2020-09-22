class Game():
    def __init__(self):
        self.board = None
        self.player1 = None
        self.player2 = None
        self.current_player = None
        self.color_schema = None
        self.last_eval = 0

    def __eq__(self, value):
        try:
            return self.board == value.board and self.player1 == value.player1 and self.player2 == value.player2
        except:
            return False
