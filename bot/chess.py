import pickle
from io import BytesIO

from cairosvg import svg2png
import chess
import chess.svg

from bot import client


class Game():
    def __init__(self):
        self.board = None
        self.player1 = None
        self.player2 = None
        self.current_player = None

    def __eq__(self, value):
        try:
            return self.board == value.board and self.player1 == value.player1 and self.player2 == value.player2
        except:
            return False

class Chess():

    def __init__(self, pickle_filename='games.pickle'):
        self.games = []
        self.pickle_filename = pickle_filename
    
    def load_games(self):
        try:
            with open(self.pickle_filename, 'rb') as f:
                self.games = pickle.load(f)
        except FileNotFoundError:
            self.games = []
        finally:
            return self.games

    def new_game(self, usr_id1, usr_id2):
        current_players_pairs = map(lambda x: [x.player1, x.player2], self.games)
        given_players_pairs = [usr_id1, usr_id2]

        if given_players_pairs in current_players_pairs:
            return 'Game already in progress'
        
        game = Game()
        game.board = chess.Board()
        game.player1 = usr_id1
        game.player2 = usr_id2
        game.current_player = usr_id1

        self.games.append(game)
        return 'Game started! Player1, make your move'

    def make_move(self, usr_id, move_uci):
        game = next((g for g in self.games if g.current_player == usr_id), None)
        if game == None:
            return 'You are either not playing a game or it is not your move', None
        # TODO Deal with player playing multiple games at once

        try:
            move = chess.Move.from_uci(move_uci)
            list(game.board.legal_moves).index(move)
        except:
            return 'Invalid move', None

        game.board.push(move)
        if game.board.is_game_over(claim_draw=True):
            return 'Game over!', None
        
        game.current_player = game.player1 if usr_id == game.player2 else game.player2
        board_png_bytes = self._build_png_board(game)
        return f'It\'s your turn, {game.current_player}', board_png_bytes

    def _build_png_board(self, game):
        png_bytes = svg2png(bytestring=chess.svg.board(board=game.board))
        return BytesIO(png_bytes)

    def save_games(self):
        with open(self.pickle_filename, 'wb') as f:
            pickle.dump(self.games, f)
