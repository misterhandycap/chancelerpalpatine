from io import StringIO

from chess import Board, WHITE
from chess.pgn import Game as PGN
from chess.pgn import read_game

from bot.models.chess_game import ChessGame
from bot.models.user import User
from bot.utils import convert_users_to_players


class Game():
    def __init__(self):
        self.id = None
        self.board = None
        self.player1 = None
        self.player2 = None
        self.current_player = None
        self.result = '*'
        self.color_schema = None
        self.last_eval = 0
        self.cpu_level = None

    def __eq__(self, value):
        try:
            return self.board == value.board and self.player1 == value.player1 and self.player2 == value.player2
        except:
            return False

    def save(self, db_session):
        chess_game = db_session.query(ChessGame).get(self.id) or ChessGame()
        chess_game.player1 = db_session.query(User).get(self.player1.id) or User(id=self.player1.id, name=self.player1.name)
        chess_game.player2 = db_session.query(User).get(self.player2.id) or User(id=self.player2.id, name=self.player2.name)
        pgn_game = PGN().from_board(self.board)
        chess_game.pgn = str(pgn_game)
        chess_game.result = {'1-0': 1, '0-1': -1, '1/2-1/2': 0, '*': None}[self.result]
        chess_game.color_schema = self.color_schema
        chess_game.cpu_level = self.cpu_level
        db_session.add(chess_game)
        db_session.commit()
        self.id = chess_game.id

    @classmethod
    def from_chess_game_model(cls, chess_game):
        game = Game()
        game.id = chess_game.id
        game.player1, = convert_users_to_players(chess_game.player1)
        game.player2, = convert_users_to_players(chess_game.player2)
        game.board = read_game(StringIO(chess_game.pgn)).end().board()
        game.current_player = game.player1 if game.board.turn == WHITE else game.player2
        game.color_schema = chess_game.color_schema
        game.cpu_level = chess_game.cpu_level
        return game
