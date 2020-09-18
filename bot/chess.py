import pickle
from io import BytesIO
from math import floor, pow, sqrt

from cairosvg import svg2png
from PIL import Image

import chess
import chess.svg
from bot import client
from chess.pgn import Game as ChessGame


class Game():
    def __init__(self):
        self.board = None
        self.player1 = None
        self.player2 = None
        self.current_player = None
        self.color_schema = None

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

    def new_game(self, user1, user2, color_schema=None):
        player1, player2 = self._convert_users_to_players(user1, user2)
        current_players_pairs = map(lambda x: [x.player1, x.player2], self.games)
        given_players_pairs = [player1, player2]

        if given_players_pairs in current_players_pairs:
            return 'Partida em andamento'

        game = Game()
        game.board = chess.Board()
        game.player1 = player1
        game.player2 = player2
        game.current_player = player1
        game.color_schema = color_schema

        self.games.append(game)
        return f'Partida iniciada! {player1.name}, faça seu movimento'

    def _find_current_game(self, player: Player, other_player: Player):
        game = [g for g in self.games if g.current_player == player]
        if game == []:
            raise Exception('Você ou não está na partida atual ou não é mais seu turno.')
        if len(game) > 1:
            if not other_player:
                raise Exception(f'Atualmente está jogando {len(game)} partidas. Informe contra qual jogador é este movimento.')
            game = [g for g in game if other_player in [g.player1, g.player2]]
            if game == []:
                raise Exception('Partida não encontrada.')
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
                return 'Movimento inválido', None
        except Exception as e:
            return str(e), None

        board_png_bytes = self._build_png_board(game)
        if game.board.is_game_over(claim_draw=True):
            pgn = self.generate_pgn(user, other_user)
            self.games.remove(game)
            return f'Fim de jogo!\n\n{pgn}', board_png_bytes

        game.current_player = game.player1 if player == game.player2 else game.player2
        return f'Seu turno é agora, {game.current_player.name}', board_png_bytes

    def resign(self, user, other_user=None):
        player, other_player = self._convert_users_to_players(user, other_user)
        try:
            game = self._find_current_game(player, other_player)
        except Exception as e:
            return str(e), None

        board_png_bytes = self._build_png_board(game)
        pgn = self.generate_pgn(user, other_user)
        self.games.remove(game)
        return f'{player.name} abandonou a partida!\n{pgn}', board_png_bytes

    def _build_png_board(self, game):
        try:
            last_move = game.board.peek()
        except IndexError:
            last_move = None
        colors = self._board_colors(game.color_schema)
        css = """
        .square.light {
            fill: %s;
        }
        .square.dark {
            fill: %s;
        }
        .square.light.lastmove {
            fill: %s;
        }
        .square.dark.lastmove {
            fill: %s;
        }
        """ % colors
        png_bytes = svg2png(bytestring=chess.svg.board(board=game.board, lastmove=last_move, style=css))
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

    def get_all_boards_png(self, page: int=0):
        full_width = 1200
        max_number_of_board_per_page = 9

        final_image = Image.new('RGB', (full_width, full_width))
        next_perfect_sqr = lambda n: int(pow(floor(sqrt(n)) + 1, 2)) if n%n**0.5 != 0 else n
        number_of_boards_sqrt = sqrt(min(next_perfect_sqr(len(self.games)), max_number_of_board_per_page))
        board_width = int(full_width / number_of_boards_sqrt)
        start_page_position = max_number_of_board_per_page * page
        
        for index, game in enumerate(self.games):
            if not index in range(start_page_position, start_page_position + max_number_of_board_per_page):
                continue
            index -= start_page_position
            board_png = self._build_png_board(game)
            board_image = Image.open(board_png)
            board_position = (board_width * int(index % number_of_boards_sqrt), board_width * int(floor(index / number_of_boards_sqrt)))
            final_image.paste(board_image.resize((board_width, board_width)), board_position)

        bytesio = BytesIO()
        final_image.save(bytesio, format="png")
        bytesio.seek(0)
        return bytesio

    def _convert_users_to_players(self, *args):
        return tuple(map(lambda user: Player(user) if user else None, args))

    def _board_colors(self, color_schema):
        colors = {
            "blue": ("#dee3e6", "#8ca2ad", "#c3d887", "#92b166"),
            "purple": ("#e7dcf1", "#967bb1", "#c7d38e", "#989a68"),
            "green": ("#ffffdd", "#86a666", "#96d6d4", "#4fa28e"),
            "red": ("#e9eab8", "#f17575", "#cbde6e", "#cd9543"),
            "gray": ("#dcdcdc", "#afafaf", "#c1d381", "#a9bb69"),
            "wood": ("#f0d9b5", "#b58863", "#cdd16a", "#aaa23b"),
        }
        default = colors["green"]
        return colors.get(color_schema, default)
