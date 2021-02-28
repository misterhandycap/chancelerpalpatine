import asyncio
import os
import warnings
from uuid import uuid4
from unittest import TestCase

import chess
from dotenv import load_dotenv

from bot.chess.chess import Chess
from bot.chess.game import Game
from bot.chess.player import Player
from bot.models.chess_game import ChessGame
from tests.support.db_connection import clear_data, Session
from tests.support.fake_discord_user import FakeDiscordUser


class TestChess(TestCase):

    @classmethod
    def setUpClass(cls):
        load_dotenv()
    
    def setUp(self):
        self.db_session = Session()
    
    def tearDown(self):
        clear_data(self.db_session)
        self.db_session.close()

    def test_load_games_entries_exist(self):
        warnings.simplefilter('ignore')
        board1 = chess.Board()
        board1.push_san("e4")
        board1.push_san("e5")
        game1 = Game()
        game1.board = board1
        game1.player1 = FakeDiscordUser(id=1)
        game1.player2 = FakeDiscordUser(id=2)
        asyncio.run(game1.save())
        board2 = chess.Board()
        board2.push_san("Nf3")
        game2 = Game()
        game2.board = board2
        game2.player1 = FakeDiscordUser(id=2)
        game2.player2 = FakeDiscordUser(id=3)
        asyncio.run(game2.save())
        game3 = Game()
        game3.board = chess.Board('rnbqkbnr/ppppp2p/8/5ppQ/4P3/2N5/PPPP1PPP/R1B1KBNR b KQkq - 0 1')
        game3.player1 = FakeDiscordUser(id=2)
        game3.player2 = FakeDiscordUser(id=3)
        game3.result = '1-0'
        asyncio.run(game3.save())

        expected_games = [game1, game2]

        chess_bot = Chess()

        actual = asyncio.run(chess_bot.load_games())

        self.assertListEqual(expected_games, actual)

    def test_load_games_no_entries_exist(self):
        chess_bot = Chess()
        
        actual = asyncio.run(chess_bot.load_games())
        
        self.assertEqual([], actual)

    def test_new_game_new_players(self):
        player1 = FakeDiscordUser(id=1)
        player2 = FakeDiscordUser(id=2)

        chess_bot = Chess()
        result = chess_bot.new_game(player1, player2)
        games = chess_bot.games

        self.assertIn('Partida iniciada', result)
        self.assertEqual(len(games), 1)
        self.assertEqual(games[0].player1, player1)
        self.assertEqual(games[0].player2, player2)
        self.assertEqual(games[0].board.move_stack, [])
        self.assertIsNone(games[0].color_schema)

    def test_new_game_with_color_schema(self):
        player1 = FakeDiscordUser(id=1)
        player2 = FakeDiscordUser(id=2)
        color_schema = "blue"

        chess_bot = Chess()
        result = chess_bot.new_game(player1, player2, color_schema=color_schema)
        games = chess_bot.games

        self.assertIn('Partida iniciada', result)
        self.assertEqual(len(games), 1)
        self.assertEqual(games[0].player1, player1)
        self.assertEqual(games[0].player2, player2)
        self.assertEqual(games[0].board.move_stack, [])
        self.assertEqual(games[0].color_schema, color_schema)

    def test_new_game_pve(self):
        player1 = FakeDiscordUser(id=1)

        chess_bot = Chess()
        result = chess_bot.new_game(player1, None, cpu_level=5)
        games = chess_bot.games

        self.assertIn('Partida iniciada', result)
        self.assertEqual(len(games), 1)
        self.assertEqual(games[0].player1, player1)
        self.assertEqual(games[0].player2, None)
        self.assertEqual(games[0].board.move_stack, [])
        self.assertEqual(games[0].cpu_level, 5)
        self.assertIsNone(games[0].color_schema)

    def test_new_game_game_already_started(self):
        game = Game()
        game.player1 = FakeDiscordUser(id=1)
        game.player2 = FakeDiscordUser(id=2)

        chess_bot = Chess()
        chess_bot.games.append(game)

        result = chess_bot.new_game(game.player1, game.player2)
        self.assertIn('Partida em andamento', result)
        self.assertEqual(len(chess_bot.games), 1)

    def test_find_current_game_in_players_turn_no_ambiguity(self):
        board = chess.Board()
        board.push_san("e4")
        board.push_san("e5")
        game = Game()
        game.board = board
        game.player1 = FakeDiscordUser(id=1)
        game.player2 = FakeDiscordUser(id=2)
        game.current_player = game.player1

        chess_bot = Chess()
        chess_bot.games.append(game)

        result = chess_bot.find_current_game(user=game.player1)

        self.assertEqual(result, game)

    def test_find_current_game_in_players_turn_with_amibiguity(self):
        chess_bot = Chess()

        board = chess.Board()
        board.push_san("e4")
        board.push_san("e5")
        game1 = Game()
        game1.board = board
        game1.player1 = FakeDiscordUser(id=1)
        game1.player2 = FakeDiscordUser(id=2)
        game1.current_player = game1.player1
        chess_bot.games.append(game1)

        game2 = Game()
        game2.board = board
        game2.player1 = FakeDiscordUser(id=1)
        game2.player2 = FakeDiscordUser(id=3)
        game2.current_player = game2.player1
        chess_bot.games.append(game2)

        with self.assertRaises(Exception) as e:
            chess_bot.find_current_game(user=game1.player1)

            self.assertIn("Informe contra qual jogador", str(e))

    def test_find_current_game_in_players_turn_amibiguity_solved(self):
        chess_bot = Chess()

        board = chess.Board()
        board.push_san("e4")
        board.push_san("e5")
        game1 = Game()
        game1.board = board
        game1.player1 = FakeDiscordUser(id=1)
        game1.player2 = FakeDiscordUser(id=2)
        game1.current_player = game1.player1
        chess_bot.games.append(game1)

        game2 = Game()
        game2.board = board
        game2.player1 = FakeDiscordUser(id=1)
        game2.player2 = FakeDiscordUser(id=3)
        game2.current_player = game2.player1
        chess_bot.games.append(game2)

        result = chess_bot.find_current_game(user=game1.player1, other_user=game1.player2)

        self.assertEqual(result, game1)

    def test_find_current_game_player_playing_themselves_and_others(self):
        chess_bot = Chess()

        board = chess.Board()
        board.push_san("e4")
        board.push_san("e5")
        game1 = Game()
        game1.board = board
        game1.player1 = FakeDiscordUser(id=1)
        game1.player2 = FakeDiscordUser(id=2)
        game1.current_player = game1.player1
        chess_bot.games.append(game1)

        game2 = Game()
        game2.board = board
        game2.player1 = FakeDiscordUser(id=1)
        game2.player2 = FakeDiscordUser(id=1)
        game2.current_player = game2.player1
        chess_bot.games.append(game2)

        result = chess_bot.find_current_game(user=game2.player1, other_user=game2.player2)

        self.assertEqual(result, game2)

    def test_find_current_game_player_not_playing(self):
        chess_bot = Chess()
        
        with self.assertRaises(Exception) as e:
            chess_bot.find_current_game(user=FakeDiscordUser(id=3))

            self.assertIn("não é mais seu turno", str(e))

    def test_find_current_game_other_player_not_found(self):
        chess_bot = Chess()

        board = chess.Board()
        board.push_san("e4")
        board.push_san("e5")
        game1 = Game()
        game1.board = board
        game1.player1 = FakeDiscordUser(id=1)
        game1.player2 = FakeDiscordUser(id=2)
        game1.current_player = game1.player1
        chess_bot.games.append(game1)

        game2 = Game()
        game2.board = board
        game2.player1 = FakeDiscordUser(id=1)
        game2.player2 = FakeDiscordUser(id=3)
        game2.current_player = game2.player1
        chess_bot.games.append(game2)

        with self.assertRaises(Exception) as e:
            chess_bot.find_current_game(user=FakeDiscordUser(id=14))

            self.assertIn("Partida não encontrada", str(e))
    
    def test_make_move_legal_uci_move_in_players_turn(self):
        board = chess.Board()
        board.push_san("e4")
        board.push_san("e5")
        game = Game()
        game.board = board
        game.player1 = FakeDiscordUser(id=1)
        game.player2 = FakeDiscordUser(id=2)
        game.current_player = game.player1

        chess_bot = Chess()
        chess_bot.games.append(game)
        result, result_board = asyncio.run(chess_bot.make_move(game, 'g1f3'))

        self.assertIn("Seu turno é agora", result)
        self.assertEqual(len(game.board.move_stack), 3)
        self.assertEqual(game.current_player, game.player2)
        
        with open(os.path.join('tests', 'support', 'make_move_legal_move.png'), 'rb') as f:
            self.assertEqual(result_board.getvalue(), f.read())

    def test_make_move_legal_san_move_in_players_turn(self):
        board = chess.Board()
        board.push_san("e4")
        board.push_san("e5")
        game = Game()
        game.board = board
        game.player1 = FakeDiscordUser(id=1)
        game.player2 = FakeDiscordUser(id=2)
        game.current_player = game.player1

        chess_bot = Chess()
        chess_bot.games.append(game)
        result, result_board = asyncio.run(chess_bot.make_move(game, 'Nf3'))

        self.assertIn("Seu turno é agora", result)
        self.assertEqual(len(game.board.move_stack), 3)
        self.assertEqual(game.current_player, game.player2)

        with open(os.path.join('tests', 'support', 'make_move_legal_move.png'), 'rb') as f:
            self.assertEqual(result_board.getvalue(), f.read())

    def test_make_move_finish_game(self):
        board = chess.Board()
        board.push_san("g4")
        board.push_san("e5")
        board.push_san("f4")
        game = Game()
        game.board = board
        game.player1 = FakeDiscordUser(id=1)
        game.player2 = FakeDiscordUser(id=2)
        game.current_player = game.player1

        chess_bot = Chess()
        chess_bot.games.append(game)
        result, result_board = asyncio.run(chess_bot.make_move(game, 'd8h4'))

        self.assertIn("Fim de jogo", result)
        self.assertIn("1. g4 e5 2. f4 Qh4# 0-1", result)
        self.assertEqual(len(chess_bot.games), 0)
        self.assertEqual(self.db_session.query(ChessGame).filter_by(result=-1).count(), 1)
        with open(os.path.join('tests', 'support', 'make_move_finish_game.png'), 'rb') as f:
            self.assertEqual(result_board.getvalue(), f.read())

    def test_make_move_legal_move_pve(self):
        board = chess.Board('rn2kb1r/pp1qpppp/2ppbn2/1B6/3PP3/2N2N2/PPP2PPP/R1BQK2R w KQkq - 0 6')
        game = Game()
        game.board = board
        game.player1 = FakeDiscordUser(id=1)
        game.player2 = FakeDiscordUser(id=2)
        game.current_player = game.player1
        game.cpu_level = 0

        chess_bot = Chess()
        chess_bot.games.append(game)
        chess_bot.stockfish_limit['time'] = 1
        result, result_board = asyncio.run(chess_bot.make_move(game, 'b5d3'))

        self.assertIn("Seu turno é agora", result)
        if chess_bot.is_stockfish_enabled():
            self.assertEqual(len(game.board.move_stack), 2)
            self.assertEqual(game.current_player, game.player1)

    def test_make_move_finish_game_pve_player_loses(self):
        board = chess.Board()
        board.push_san("g4")
        board.push_san("e5")
        game = Game()
        game.board = board
        game.player1 = FakeDiscordUser(id=1)
        game.player2 = FakeDiscordUser(id=2)
        game.current_player = game.player1
        game.cpu_level = 20

        chess_bot = Chess()
        chess_bot.games.append(game)
        result, result_board = asyncio.run(chess_bot.make_move(game, 'f4'))

        if chess_bot.is_stockfish_enabled():
            self.assertIn("Fim de jogo", result)
            self.assertIn("1. g4 e5 2. f4 Qh4# 0-1", result)
            self.assertEqual(len(chess_bot.games), 0)
            self.assertEqual(self.db_session.query(ChessGame).filter_by(result=-1).count(), 1)
            with open(os.path.join('tests', 'support', 'make_move_finish_game.png'), 'rb') as f:
                self.assertEqual(result_board.getvalue(), f.read())

    def test_make_move_finish_game_pve_player_wins(self):
        board = chess.Board()
        board.push_san("e4")
        board.push_san("g5")
        board.push_san("d4")
        board.push_san("f5")
        game = Game()
        game.board = board
        game.player1 = FakeDiscordUser(id=1)
        game.player2 = FakeDiscordUser(id=2)
        game.current_player = game.player1
        game.cpu_level = 20

        chess_bot = Chess()
        chess_bot.games.append(game)
        result, result_board = asyncio.run(chess_bot.make_move(game, 'Qh5'))

        self.assertIn("Fim de jogo", result)
        self.assertIn("1. e4 g5 2. d4 f5 3. Qh5# 1-0", result)
        self.assertEqual(self.db_session.query(ChessGame).filter_by(result=1).count(), 1)
        self.assertEqual(len(chess_bot.games), 0)

    def test_make_move_illegal_move_in_players_turn(self):
        board = chess.Board()
        board.push_san("e4")
        board.push_san("e5")
        game = Game()
        game.board = board
        game.player1 = FakeDiscordUser(id=1)
        game.player2 = FakeDiscordUser(id=2)
        game.current_player = game.player1

        chess_bot = Chess()
        chess_bot.games.append(game)
        result, result_board = asyncio.run(chess_bot.make_move(game, 'invalid'))

        self.assertIn("Movimento inválido", result)
        self.assertIsNone(result_board)
        self.assertEqual(len(game.board.move_stack), 2)
        self.assertEqual(game.current_player, game.player1)

    def test_resign_game_found(self):
        board = chess.Board()
        board.push_san("e4")
        board.push_san("e5")
        board.push_san("Nf3")
        game = Game()
        game.board = board
        game.player1 = FakeDiscordUser(id=1)
        game.player2 = FakeDiscordUser(id=2)
        game.current_player = game.player1

        chess_bot = Chess()
        chess_bot.games.append(game)
        result, result_board = asyncio.run(chess_bot.resign(game))

        self.assertIn("abandonou a partida!", result)
        self.assertIn('Result "1-0"', result)
        self.assertIn(f"Id da partida: `{game.id}`", result)
        self.assertEqual(len(chess_bot.games), 0)
        self.assertEqual(self.db_session.query(ChessGame).filter_by(result=1).count(), 1)
        with open(os.path.join('tests', 'support', 'make_move_legal_move.png'), 'rb') as f:
            self.assertEqual(result_board.getvalue(), f.read())

    def test_save_games(self):
        chess_bot = Chess()
        board1 = chess.Board()
        board1.push_san("e4")
        board1.push_san("e5")
        game1 = Game()
        game1.board = board1
        game1.player1 = FakeDiscordUser(id=1)
        game1.player2 = FakeDiscordUser(id=2)
        asyncio.run(game1.save())
        board2 = chess.Board()
        board2.push_san("Nf3")
        game2 = Game()
        game2.board = board2
        game2.player1 = FakeDiscordUser(id=2)
        game2.player2 = FakeDiscordUser(id=3)
        chess_bot.games = [game1, game2]

        asyncio.run(chess_bot.save_games())

        expected = [Game.from_chess_game_model(x) for x in self.db_session.query(ChessGame)]

        self.assertEqual(chess_bot.games, expected)
        self.assertEqual(game1.color_schema, expected[0].color_schema)
        self.assertEqual(game1.cpu_level, expected[0].cpu_level)
        self.assertEqual(game2.color_schema, expected[1].color_schema)
        self.assertEqual(game2.cpu_level, expected[1].cpu_level)

    def test_generate_pgn(self):
        board = chess.Board()
        board.push_san("g4")
        board.push_san("e5")
        board.push_san("f4")
        game = Game()
        game.board = board
        game.player1 = FakeDiscordUser(id=1, name='Player1')
        game.player2 = FakeDiscordUser(id=2, name='Player2')
        game.current_player = game.player1
        game.result = game.board.result()

        chess_bot = Chess()
        chess_bot.games.append(game)
        result = chess_bot.generate_pgn(game)

        self.assertIn('[White "Player1"]', result)
        self.assertIn('[Black "Player2"]', result)
        self.assertIn('1. g4 e5 2. f4 *', result)

    def test_get_all_boards_png_one_game(self):
        chess_bot = Chess()

        board1 = chess.Board()
        board1.push_san("e4")
        board1.push_san("e5")
        board1.push_san("Bc4")
        game1 = Game()
        game1.color_schema = "green"
        game1.board = board1
        chess_bot.games.append(game1)

        image_bytesio = asyncio.run(chess_bot.get_all_boards_png())

        with open(os.path.join('tests', 'support', 'get_all_boards_png_one_game.png'), 'rb') as f:
            self.assertEqual(image_bytesio.read(), f.read())

    def test_get_all_boards_png_three_games(self):
        chess_bot = Chess()

        board1 = chess.Board()
        board1.push_san("e4")
        board1.push_san("e5")
        game1 = Game()
        game1.color_schema = "blue"
        game1.board = board1
        chess_bot.games.append(game1)

        board2 = chess.Board()
        board2.push_san("Nf3")
        board2.push_san("d6")
        game2 = Game()
        game2.color_schema = "wood"
        game2.board = board2
        chess_bot.games.append(game2)

        board3 = chess.Board()
        board3.push_san("Nf3")
        game3 = Game()
        game3.color_schema = "green"
        game3.board = board3
        chess_bot.games.append(game3)
        
        image_bytesio = asyncio.run(chess_bot.get_all_boards_png())

        with open(os.path.join('tests', 'support', 'get_all_boards_png_three_games.png'), 'rb') as f:
            self.assertEqual(image_bytesio.read(), f.read())

    def test_get_all_boards_png_no_twelve_games(self):
        chess_bot = Chess()

        board1 = chess.Board()
        board1.push_san("e4")
        board1.push_san("e5")
        game1 = Game()
        game1.color_schema = "blue"
        game1.board = board1
        chess_bot.games.append(game1)

        board2 = chess.Board()
        board2.push_san("Nf3")
        board2.push_san("d6")
        game2 = Game()
        game2.color_schema = "wood"
        game2.board = board2
        chess_bot.games.append(game2)

        board3 = chess.Board()
        board3.push_san("Nf3")
        game3 = Game()
        game3.color_schema = "green"
        game3.board = board3
        chess_bot.games.append(game3)

        for i in range(3):
            chess_bot.games.append(game1)
            chess_bot.games.append(game2)
            chess_bot.games.append(game3)

        image_bytesio = asyncio.run(chess_bot.get_all_boards_png())

        with open(os.path.join('tests', 'support', 'get_all_boards_png_twelve_games.png'), 'rb') as f:
            self.assertEqual(image_bytesio.read(), f.read())

    def test_get_all_boards_png_no_twelve_games_second_page(self):
        chess_bot = Chess()

        board1 = chess.Board()
        board1.push_san("e4")
        board1.push_san("e5")
        game1 = Game()
        game1.color_schema = "blue"
        game1.board = board1
        chess_bot.games.append(game1)

        board2 = chess.Board()
        board2.push_san("Nf3")
        board2.push_san("d6")
        game2 = Game()
        game2.color_schema = "wood"
        game2.board = board2
        chess_bot.games.append(game2)

        board3 = chess.Board()
        board3.push_san("Nf3")
        game3 = Game()
        game3.color_schema = "green"
        game3.board = board3
        chess_bot.games.append(game3)

        for i in range(3):
            chess_bot.games.append(game1)
            chess_bot.games.append(game2)
            chess_bot.games.append(game3)

        image_bytesio = asyncio.run(chess_bot.get_all_boards_png(page=2), debug=True)

        with open(os.path.join('tests', 'support', 'get_all_boards_png_twelve_games_second_page.png'), 'rb') as f:
            self.assertEqual(image_bytesio.read(), f.read())
    
    def test_get_all_boards_png_no_games_being_played(self):
        chess_bot = Chess()

        image_bytesio = asyncio.run(chess_bot.get_all_boards_png())
        
        self.assertIsNone(image_bytesio)

    def test_is_pve_game_pve_game(self):
        game = Game()
        game.cpu_level = 0

        chess_bot = Chess()
        chess_bot.stockfish_path = "valid"
        chess_bot.games.append(game)

        self.assertTrue(chess_bot.is_pve_game(game))

    def test_is_pve_game_pvp_game(self):
        game = Game()
        game.cpu_level = None

        chess_bot = Chess()
        chess_bot.stockfish_path = "valid"
        chess_bot.games.append(game)

        self.assertFalse(chess_bot.is_pve_game(game))

    def test_is_pve_game_stockfish_disabled(self):
        game = Game()
        game.cpu_level = 0

        chess_bot = Chess()
        chess_bot.stockfish_path = ""
        chess_bot.games.append(game)

        self.assertFalse(chess_bot.is_pve_game(game))

    def test_eval_last_move_last_move_blunder_mate_in_one(self):
        board = chess.Board()
        board.push_san("g4")
        board.push_san("e5")
        board.push_san("f4")
        game = Game()
        game.board = board
        game.player1 = FakeDiscordUser(id=1)
        game.player2 = FakeDiscordUser(id=2)
        game.current_player = game.player1
        game.last_eval = 0

        chess_bot = Chess()
        chess_bot.games.append(game)
        result = asyncio.run(chess_bot.eval_last_move(game))

        if chess_bot.is_stockfish_enabled():
            self.assertTrue(result["blunder"])
            self.assertEqual(result["mate_in"], 1)
        else:
            self.assertFalse(result["blunder"])
            self.assertIsNone(result["mate_in"])
    
    def test_eval_last_move_no_blunder_no_mate(self):
        board = chess.Board()
        board.push_san("g4")
        board.push_san("e5")
        game = Game()
        game.board = board
        game.player1 = FakeDiscordUser(id=1)
        game.player2 = FakeDiscordUser(id=2)
        game.current_player = game.player1
        game.last_eval = 0

        chess_bot = Chess()
        chess_bot.games.append(game)
        chess_bot.stockfish_limit["time"] = 2

        result = asyncio.run(chess_bot.eval_last_move(game))

        self.assertFalse(result["blunder"])
        self.assertIsNone(result["mate_in"])

    def test_eval_last_move_blunder_no_mate(self):
        board = chess.Board()
        board.push_san("e4")
        board.push_san("Nf6")
        board.push_san("Qh5")
        game = Game()
        game.board = board
        game.player1 = FakeDiscordUser(id=1)
        game.player2 = FakeDiscordUser(id=2)
        game.current_player = game.player1
        game.last_eval = 0

        chess_bot = Chess()
        chess_bot.games.append(game)
        chess_bot.stockfish_limit["time"] = 2

        result = asyncio.run(chess_bot.eval_last_move(game))

        if chess_bot.is_stockfish_enabled():
            self.assertTrue(result["blunder"])
        else:
            self.assertFalse(result['blunder'])
        self.assertIsNone(result["mate_in"])

    def test_eval_last_move_no_blunder_mate_in_two(self):
        board = chess.Board("Q2r4/1p1k4/1P3ppp/1Kp1r3/4p2b/1B3P2/2P2q2/8 w - - 6 44")
        game = Game()
        game.board = board
        game.player1 = FakeDiscordUser(id=1)
        game.player2 = FakeDiscordUser(id=2)
        game.current_player = game.player1
        game.last_eval = 1500

        chess_bot = Chess()
        chess_bot.games.append(game)

        result = asyncio.run(chess_bot.eval_last_move(game))

        self.assertFalse(result["blunder"])
        if chess_bot.is_stockfish_enabled():
            self.assertEqual(result["mate_in"], 2)
        else:
            self.assertIsNone(result["mate_in"])

    def test_eval_last_move_no_blunder_mate_in_two_against_current_player(self):
        board = chess.Board("Q1kr4/1p6/1P3ppp/1Kp1r3/4p2b/1B3P2/2P2q2/8 b - - 5 43")
        game = Game()
        game.board = board
        game.player1 = FakeDiscordUser(id=1)
        game.player2 = FakeDiscordUser(id=2)
        game.current_player = game.player1
        game.last_eval = 1500

        chess_bot = Chess()
        chess_bot.games.append(game)

        result = asyncio.run(chess_bot.eval_last_move(game))

        self.assertFalse(result["blunder"])
        if chess_bot.is_stockfish_enabled():
            self.assertEqual(result["mate_in"], -2)
        else:
            self.assertIsNone(result["mate_in"])

    def test_build_animated_sequence_gif_valid_params(self):
        board = chess.Board()
        board.push_san('e4')
        board.push_san('c5')
        board.push_san('Nc3')
        game = Game()
        game.board = board
        game.player1 = FakeDiscordUser(id=1)
        game.player2 = FakeDiscordUser(id=2)

        chess_bot = Chess()
        chess_bot.games.append(game)
        sequence = ['Nf3', 'd6', 'd4', 'cxd4', 'Nxd4', 'Nf6', 'Nc3', 'a6']

        result = asyncio.run(chess_bot.build_animated_sequence_gif(game, 2, sequence))

        with open(os.path.join('tests', 'support', 'build_animated_sequence_gif.gif'), 'rb') as f:
            self.assertEqual(result.getvalue(), f.read())

    def test_build_animated_sequence_gif_invalid_move_in_sequence(self):
        board = chess.Board()
        board.push_san('e4')
        board.push_san('c5')
        board.push_san('Nc3')
        game = Game()
        game.board = board
        game.player1 = FakeDiscordUser(id=1)
        game.player2 = FakeDiscordUser(id=2)

        chess_bot = Chess()
        chess_bot.games.append(game)
        sequence = ['Nf3', 'd6', 'd4', 'Rxa8', 'Nxd4', 'Nf6', 'Nc3', 'a6']

        result = asyncio.run(chess_bot.build_animated_sequence_gif(game, 2, sequence))

        self.assertIsNone(result)

    def test_get_game_by_id_game_exists(self):
        warnings.simplefilter('ignore')
        board1 = chess.Board()
        board1.push_san("e4")
        board1.push_san("e5")
        game1 = Game()
        game1.board = board1
        game1.player1 = FakeDiscordUser(id=1)
        game1.player2 = FakeDiscordUser(id=2)
        asyncio.run(game1.save())

        result = asyncio.run(Chess().get_game_by_id(game1.id))

        self.assertEqual(result, game1)

    def test_get_game_by_id_game_does_not_exist(self):
        warnings.simplefilter('ignore')
        board1 = chess.Board()
        board1.push_san("e4")
        board1.push_san("e5")
        game1 = Game()
        game1.board = board1
        game1.player1 = FakeDiscordUser(id=1)
        game1.player2 = FakeDiscordUser(id=2)
        asyncio.run(game1.save())

        result = asyncio.run(Chess().get_game_by_id(uuid4()))

        self.assertIsNone(result)

    def test_get_game_by_id_game_invalid_uuid(self):
        warnings.simplefilter('ignore')
        board1 = chess.Board()
        board1.push_san("e4")
        board1.push_san("e5")
        game1 = Game()
        game1.board = board1
        game1.player1 = FakeDiscordUser(id=1)
        game1.player2 = FakeDiscordUser(id=2)
        asyncio.run(game1.save())

        result = asyncio.run(Chess().get_game_by_id("invalid_id"))

        self.assertIsNone(result)
