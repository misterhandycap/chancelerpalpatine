class ChessException(Exception):
    def __init__(self, message, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.message = message


class GameNotFound(ChessException):
    def __init__(self, *args, **kwargs):
        super().__init__("Game not found", *args, **kwargs)


class GameAlreadyInProgress(ChessException):
    def __init__(self, *args, **kwargs):
        super().__init__("Game already in progress", *args, **kwargs)


class MultipleGamesAtOnce(ChessException):
    def __init__(self, number_of_games, *args, **kwargs):
        super().__init__(
            'You are currently playing {number_of_games} games. '\
                'Please provide your opponent to whom you whish to play this move.', *args, **kwargs)
        self.number_of_games = number_of_games


class NoGamesWithPlayer(ChessException):
    def __init__(self, *args, **kwargs):
        super().__init__("You are either not playing a game or it is not your turn anymore", *args, **kwargs)


class InvalidMove(ChessException):
    def __init__(self, *args, **kwargs):
        super().__init__("Invalid move", *args, **kwargs)


class PuzzleNotFound(ChessException):
    def __init__(self, *args, **kwargs):
        super().__init__("Puzzle not found", *args, **kwargs)
