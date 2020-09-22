import os
import pickle
from io import BytesIO
from math import floor, pow, sqrt

import asyncssh
from cairosvg import svg2png
from PIL import Image

import chess
import chess.engine
import chess.svg
from chess.pgn import Game as ChessGame

from bot import client
from bot.chess.game import Game
from bot.chess.player import Player


class Chess():

    def __init__(self, pickle_filename='games.pickle'):
        self.games = []
        self.pickle_filename = pickle_filename
        self.stockfish_path = os.environ.get("STOCKFISH_PATH_EXE", '')
        self.stockfish_limit = {
            "time": int(os.environ.get("STOCKFISH_TIME_LIMIT", '5')),
            "depth": int(os.environ.get("STOCKFISH_DEPTH_LIMIT", '20'))
        }
        self.stockfish_ssh = {
            "host": os.environ.get("STOCKFISH_SSH_HOST"),
            "username": os.environ.get("STOCKFISH_SSH_USER"),
            "password": os.environ.get("STOCKFISH_SSH_PASSWORD"),
            "port": int(os.environ.get("STOCKFISH_SSH_PORT", '22')),
            "known_hosts": None
        }

    def load_games(self):
        """
        Load all ongoing games from pickle file

        :return: List of ongoing games
        :rtype: List[Games]
        """
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

    def find_current_game(self, user, other_user=None):
        """
        Get users' current game. Second user may be necessary if player1 is playing
        more than one game at a time.

        :param user: Next player to move
        :type user: discord.User
        :param other_user: Next player's opponent
        :type other_user: discord.User
        :return: Current game
        :rtype: Game
        :raises Exception: Game not found or invalid parameters
        """
        player, other_player = self._convert_users_to_players(user, other_user)
        game = [g for g in self.games if g.current_player == player]
        if game == []:
            raise Exception('Você ou não está na partida atual ou não é mais seu turno.')
        if len(game) > 1:
            if not other_player:
                raise Exception(f'Atualmente está jogando {len(game)} partidas. Informe contra qual jogador é este movimento.')
            game = [g for g in game if set([player.id, other_player.id]) == set([g.player1.id, g.player2.id])]
            if game == []:
                raise Exception('Partida não encontrada.')
        return game[0]

    def make_move(self, game: Game, move: str):
        """
        Makes a move in given game, if valid

        :param game: Game to be played
        :type game: Game
        :param move: Chess move in SAN or UCI notation
        :type move: str
        :return: Bot message and PNG board
        :rtype: Tuple[str, BytesIO]
        """
        try:
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
            pgn = self.generate_pgn(game)
            self.games.remove(game)
            return f'Fim de jogo!\n\n{pgn}', board_png_bytes

        game.current_player = game.player1 if game.current_player == game.player2 else game.player2
        return f'Seu turno é agora, {game.current_player.name}', board_png_bytes

    def resign(self, game: Game):
        """
        Resigns the given game. Only the next player to move can resign their game.

        :param game: Game to be resigned
        :type game: Game
        :return: Bot message
        :rtype: str
        """
        board_png_bytes = self._build_png_board(game)
        pgn = self.generate_pgn(game)
        self.games.remove(game)
        return f'{game.current_player.name} abandonou a partida!\n{pgn}', board_png_bytes

    def save_games(self):
        """
        Save all ongoing games into pickle file
        """
        with open(self.pickle_filename, 'wb') as f:
            pickle.dump(self.games, f)

    def generate_pgn(self, game: Game):
        """
        Gets PGN for given game

        :param game: Current game
        :type game: Game
        :return: Bot message formatted with PGN
        :rtype: str
        """
        chess_game = ChessGame()
        chess_game.headers["White"] = str(game.player1.name)
        chess_game.headers["Black"] = str(game.player2.name)
        chess_game.headers["Result"] = str(game.board.result())
        last_node = chess_game
        for move in game.board.move_stack:
            last_node = last_node.add_variation(move)

        return f"```\n{str(chess_game)}\n```"

    def get_all_boards_png(self, page: int=0):
        """
        Gets an image showing all ongoing games' current position.
        If there are more than 9 games being played at once, this
        command is paginated.

        :param page: Page index (defaults to 0)
        :type page: int
        :return: Image's bytesIO
        :rtype: BytesIO
        """
        full_width = 1200
        max_number_of_board_per_page = 9

        if not self.games:
            return None

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

    def is_stockfish_enabled(self):
        """
        Returns whether Stockfish is enabled on this environment

        :rtype: bool
        """
        return self.stockfish_path
    
    async def eval_last_move(self, game: Game):
        """
        Evaluates last played move in given game.
        Returns a dictonary containing information such as whether
        last move was a blunder and if there are any forcing mate
        sequences.

        :param game: Game to be analized
        :type game: Game
        :return: Last move evaluation
        :rtype: Dict
        """
        eval_dict = {
            "blunder": False,
            "mate_in": None,
        }
        
        if not self.is_stockfish_enabled():
            return eval_dict
        
        analysis = await self._eval_game(game)
        eval_dict["blunder"] = self._is_last_move_blunder(game, analysis)
        eval_dict["mate_in"] = analysis["score"].relative.mate()
        return eval_dict
    
    def _is_last_move_blunder(self, game: Game, analysis: dict):
        last_eval = game.last_eval
        game.last_eval = analysis["score"].white().score(mate_score=1500)
        return abs(game.last_eval - last_eval) > 200
    
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
    
    async def _eval_game(self, game: Game):
        limit = chess.engine.Limit(**self.stockfish_limit)
        if self.stockfish_ssh["host"]:
            async with asyncssh.connect(**self.stockfish_ssh) as conn:
                _channel, engine = await conn.create_subprocess(chess.engine.UciProtocol, self.stockfish_path)
                await engine.initialize()
                return await engine.analyse(game.board, limit)
        else:
            with chess.engine.SimpleEngine.popen_uci(self.stockfish_path) as engine:
                return engine.analyse(game.board, limit)

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