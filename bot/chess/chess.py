import logging
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

from bot.chess.exceptions import (GameAlreadyInProgress, GameNotFound, 
                                InvalidMove, MultipleGamesAtOnce, NoGamesWithPlayer)
from bot.chess.game import Game
from bot.chess.player import Player
from bot.models.chess_game import ChessGame as ChessGameModel
from bot.utils import convert_users_to_players, paginate, run_cpu_bound_task


class Chess():

    def __init__(self):
        self.games = []
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

    async def load_games(self):
        """
        Load all ongoing games from database

        :return: List of ongoing games
        :rtype: List[Games]
        """
        try:
            chess_games_models = await ChessGameModel.get_all_ongoing_games()
            self.games = [Game.from_chess_game_model(x) for x in chess_games_models]
        except Exception as e:
            logging.warning(e, exc_info=True)
        finally:
            return self.games

    async def get_game_by_id(self, chess_game_id: str) -> Game:
        """
        Fetches from database chess game by given chess game id

        :param chess_game_id: Chess game's UUID
        :type chess_game_id: str
        :return: Chess game
        :rtype: Game
        """
        try:
            chess_game_model = await ChessGameModel.get(
                chess_game_id, preload_players=True)
            if not chess_game_model:
                return None
        except:
            return None
        return Game.from_chess_game_model(chess_game_model)

    def new_game(self, user1, user2, color_schema=None, cpu_level=None):
        player1, player2 = convert_users_to_players(user1, user2)
        current_players_pairs = map(lambda x: [x.player1, x.player2], self.games)
        given_players_pairs = [player1, player2]

        if given_players_pairs in current_players_pairs:
            raise GameAlreadyInProgress()

        game = Game()
        game.board = chess.Board()
        game.player1 = player1
        game.player2 = player2
        game.current_player = player1
        game.result = game.board.result()
        game.color_schema = color_schema
        game.cpu_level = cpu_level

        self.games.append(game)
        return game

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
        :raises NoGamesWithPlayer: Game not found when other_user is not given
        :raises MultipleGamesAtOnce: Given user is playing multiple games currently
        :raises GameNotFound: No game with given user and other_user was found
        """
        player, other_player = convert_users_to_players(user, other_user)
        game = [g for g in self.games if g.current_player == player]
        if game == []:
            raise NoGamesWithPlayer()
        if len(game) > 1:
            if not other_player:
                raise MultipleGamesAtOnce(number_of_games=len(game))
            game = [g for g in game if set([player.id, other_player.id]) == set([g.player1.id, g.player2.id])]
            if game == []:
                raise GameNotFound()
        return game[0]

    async def make_move(self, game: Game, move: str) -> Game:
        """
        Makes a move in given game, if valid

        :param game: Game to be played
        :type game: Game
        :param move: Chess move in SAN or UCI notation
        :type move: str
        :return: Updated game
        :rtype: Game
        """
        chess_move = self._parse_str_move(game, move)
        if not chess_move:
            raise InvalidMove()
        game.board.push(chess_move)

        game.current_player = game.player1 if game.current_player == game.player2 else game.player2

        if self.is_pve_game(game) and not self.is_game_over(game):
            stockfish_result = await self._play_move(game)
            game.board.push(stockfish_result.move)
            game.current_player = game.player1
        
        if self.is_game_over(game):
            game.result = game.board.result()
            self.games.remove(game)
            
        await game.save()
        return game

    def is_game_over(self, game: Game) -> bool:
        """
        Checks whether given game is over

        :param game: Game to be checked
        :type game: Game
        :return: True if game is over and False otherwise
        :rtype: Bool
        """
        return game.board.is_game_over(claim_draw=True)
    
    async def resign(self, game: Game) -> Game:
        """
        Resigns the given game. Only the next player to move can resign their game.

        :param game: Game to be resigned
        :type game: Game
        :return: Updated game
        :rtype: Game
        """
        board_png_bytes = self.build_png_board(game)
        game.result = '0-1' if game.board.turn == chess.WHITE else '1-0'
        await game.save()
        self.games.remove(game)
        return game

    async def save_games(self):
        """
        Save all ongoing games into database
        """
        for game in self.games:
            await game.save()

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
        chess_game.headers["Result"] = str(game.result)
        last_node = chess_game
        for move in game.board.move_stack:
            last_node = last_node.add_variation(move)

        result = f"```\n{str(chess_game)}\n```"
        if game.id:
            result += f'Game id: `{game.id}`'
        return result

    @run_cpu_bound_task
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
        paginated_games, _ = paginate(self.games, page, max_number_of_board_per_page)
        
        for index, game in enumerate(paginated_games):
            board_png = self.build_png_board(game)
            board_image = Image.open(board_png)
            board_position = (board_width * int(index % number_of_boards_sqrt), board_width * int(floor(index / number_of_boards_sqrt)))
            final_image.paste(board_image.resize((board_width, board_width)), board_position)

        bytesio = BytesIO()
        final_image.save(bytesio, format="png")
        bytesio.seek(0)
        return bytesio

    def is_pve_game(self, game: Game):
        """
        Returns whether given game is PvE or not
        """
        return game.cpu_level is not None and self.is_stockfish_enabled()
    
    def is_stockfish_enabled(self):
        """
        Returns whether Stockfish is enabled on this environment

        :rtype: bool
        """
        return bool(self.stockfish_path)
    
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
    
    def build_png_board(self, game: Game) -> BytesIO:
        """
        Builds a PNG for current given game's board position

        :param game: Game with position to be displayed
        :type game: Game
        :return: PNG image's bytes
        :rtype: BytesIO
        """
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

    @run_cpu_bound_task
    def build_animated_sequence_gif(self, game: Game, game_move: int, sequence: list) -> BytesIO:
        """
        Builds an animated GIF for illustrating a given game's possible variation

        :param game: Game to be used for variation
        :type game: Game
        :param game_move: Number of game's move for the start of variation
        :type game_move: int
        :param sequence: Variation's sequence of move
        :type sequence: str[]
        :return: Animated gif's bytesIO
        :rtype: BytesIO
        """
        game_moves = game.board.move_stack
        new_board = chess.Board()
        new_game = Game()
        new_game.board = new_board
        new_game.color_schema = game.color_schema
        for move in game_moves[:game_move]:
            new_board.push(move)
        
        first_gif_frame = Image.open(self.build_png_board(new_game))
        gif_frames = []
        for variant_move in sequence:
            variant_chess_move = self._parse_str_move(new_game, variant_move)
            if not variant_chess_move:
                return
            new_board.push(variant_chess_move)
            gif_frame = Image.open(self.build_png_board(new_game))
            gif_frames.append(gif_frame)
        
        bytesio = BytesIO()
        first_gif_frame.save(
            bytesio,
            format='gif',
            save_all=True,
            append_images=gif_frames,
            duration=1000,
            loop=0
        )
        bytesio.seek(0)
        return bytesio
    
    def _parse_str_move(self, game: Game, move: str) -> chess.Move:
        try:
            return game.board.parse_uci(move)
        except ValueError:
            try:
                return game.board.parse_san(move)
            except ValueError:
                return None
        except Exception as e:
            logging.warning(e)
            return None
    
    def _is_last_move_blunder(self, game: Game, analysis: dict):
        last_eval = game.last_eval
        game.last_eval = analysis["score"].white().score(mate_score=1500)
        return abs(game.last_eval - last_eval) > 200
    
    async def _eval_game(self, game: Game):
        limit = chess.engine.Limit(**self.stockfish_limit)
        if self.stockfish_ssh["host"]:
            async with asyncssh.connect(**self.stockfish_ssh) as conn:
                _channel, engine = await conn.create_subprocess(chess.engine.UciProtocol, self.stockfish_path)
                await engine.initialize()
                return await engine.analyse(game.board, limit)
        else:
            try:
                transport, engine = await chess.engine.popen_uci(self.stockfish_path)
                return await engine.analyse(game.board, limit)
            finally:
                await engine.quit()
                transport.close()

    async def _play_move(self, game: Game):
        limit = chess.engine.Limit(**self.stockfish_limit)
        if self.stockfish_ssh["host"]:
            async with asyncssh.connect(**self.stockfish_ssh) as conn:
                _channel, engine = await conn.create_subprocess(chess.engine.UciProtocol, self.stockfish_path)
                await engine.initialize()
                return await engine.play(game.board, limit, options={'Skill level': game.cpu_level})
        else:
            try:
                transport, engine = await chess.engine.popen_uci(self.stockfish_path)
                return await engine.play(game.board, limit, options={'Skill level': game.cpu_level})
            finally:
                await engine.quit()
                transport.close()

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
