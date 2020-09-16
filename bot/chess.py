import pickle
from io import BytesIO

from cairosvg import svg2png
import chess
import chess.svg
from chess.pgn import Game as ChessGame

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


class Player():
    def __init__(self, user):
        self.id = user.id
        self.name = user.name

    def __eq__(self, value):
        try:
            return self.id == value.id
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

    def new_game(self, user1, user2):
        player1, player2 = self._convert_users_to_players(user1, user2)
        current_players_pairs = map(lambda x: [x.player1, x.player2], self.games)
        given_players_pairs = [player1, player2]

        if given_players_pairs in current_players_pairs:
            return 'Game already in progress'
        
        game = Game()
        game.board = chess.Board()
        game.player1 = player1
        game.player2 = player2
        game.current_player = player1

        self.games.append(game)
        return f'Game started! {player1.name}, make your move'

    def _find_current_game(self, player: Player, other_player: Player):
        game = [g for g in self.games if g.current_player == player]
        if game == []:
            raise Exception('You are either not playing a game or it is not your move')
        if len(game) > 1:
            if not other_player:
                raise Exception(f'You are currently playing {len(game)} games. Please tell which player you\'re facing.')
            game = [g for g in game if other_player in [g.player1, g.player2]]
            if game == []:
                raise Exception('Game not found')
        return game[0]
    
    def make_move(self, user, move, other_user=None):
        player, other_player = self._convert_users_to_players(user, other_user)
        try:
            game = self._find_current_game(player, other_player)
            game.board.push_uci(move)
        except ValueError:
            try:
                game.board.push_san(move)
            except ValueError:
                return 'Invalid move', None
        except Exception as e:
            return str(e), None

        board_png_bytes = self._build_png_board(game)
        if game.board.is_game_over(claim_draw=True):
            pgn = self.generate_pgn(user, other_user)
            self.games.remove(game)
            return f'Game over!\n\n{pgn}', board_png_bytes
        
        game.current_player = game.player1 if player == game.player2 else game.player2
        return f'It\'s your turn, {game.current_player.name}', board_png_bytes

    def resign(self, user, other_user=None):
        player, other_player = self._convert_users_to_players(user, other_user)
        try:
            game = self._find_current_game(player, other_player)
        except Exception as e:
            return str(e), None
        
        board_png_bytes = self._build_png_board(game)
        self.games.remove(game)
        return f'{player.name} resign the game!', board_png_bytes
    
    def _build_png_board(self, game):
        try:
            last_move = game.board.peek()
        except IndexError:
            last_move = None
        png_bytes = svg2png(bytestring=chess.svg.board(board=game.board, lastmove=last_move))
        return BytesIO(png_bytes)

    def save_games(self):
        with open(self.pickle_filename, 'wb') as f:
            pickle.dump(self.games, f)

    def generate_pgn(self, user, other_user=None):
        try:
            player, other_player = self._convert_users_to_players(user, other_user)
            game = self._find_current_game(player, other_player)
        except Exception as e:
            return str(e)
            
        chess_game = ChessGame()
        chess_game.headers["White"] = str(game.player1.name)
        chess_game.headers["Black"] = str(game.player2.name)
        chess_game.headers["Result"] = str(game.board.result())
        last_node = chess_game
        for move in game.board.move_stack:
            last_node = last_node.add_variation(move)

        return f"```\n{str(chess_game)}\n```"

    def _convert_users_to_players(self, *args):
        return tuple(map(lambda user: Player(user) if user else None, args))
