import asyncio
import os
import pickle
from unittest import TestCase

import chess
from dotenv import load_dotenv

from bot.chess.chess import Chess
from bot.chess.game import Game
from bot.chess.player import Player
from tests.support.fake_discord_user import FakeDiscordUser

PICKLE_FILENAME = 'games_test.pickle'


class TestChess(TestCase):

    @classmethod
    def setUpClass(cls):
        load_dotenv()
    
    def tearDown(self):
        try:
            os.remove(PICKLE_FILENAME)
        except FileNotFoundError:
            pass

    def test_load_games_file_exists(self):
        board1 = chess.Board()
        board1.push_san("e4")
        board1.push_san("e5")
        game1 = Game()
        game1.board = board1
        game1.player1 = FakeDiscordUser(id=1)
        game1.player2 = FakeDiscordUser(id=2)
        board2 = chess.Board()
        board2.push_san("Nf3")
        game2 = Game()
        game2.board = board2
        game2.player1 = FakeDiscordUser(id=2)
        game2.player2 = FakeDiscordUser(id=3)
        games = [game1, game2]

        with open(PICKLE_FILENAME, 'wb') as f:
            pickle.dump(games, f)

        chess_bot = Chess(pickle_filename=PICKLE_FILENAME)
        self.assertEqual(games, chess_bot.load_games())

    def test_load_games_file_doesnt_exist(self):
        self.assertEqual([], Chess(pickle_filename=PICKLE_FILENAME).load_games())

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
        result, result_board = chess_bot.make_move(game, 'g1f3')

        self.assertIn("Seu turno é agora", result)
        self.assertEqual(len(game.board.move_stack), 3)
        self.assertEqual(game.current_player, game.player2)
        
        with open('tests/support/make_move_legal_move.png', 'rb') as f:
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
        result, result_board = chess_bot.make_move(game, 'Nf3')

        self.assertIn("Seu turno é agora", result)
        self.assertEqual(len(game.board.move_stack), 3)
        self.assertEqual(game.current_player, game.player2)

        with open('tests/support/make_move_legal_move.png', 'rb') as f:
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
        result, result_board = chess_bot.make_move(game, 'd8h4')

        self.assertIn("Fim de jogo", result)
        self.assertIn("1. g4 e5 2. f4 Qh4# 0-1", result)
        self.assertEqual(len(chess_bot.games), 0)

        with open('tests/support/make_move_finish_game.png', 'rb') as f:
            self.assertEqual(result_board.getvalue(), f.read())

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
        result, result_board = chess_bot.make_move(game, 'invalid')

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
        result, result_board = chess_bot.resign(game)

        self.assertIn("abandonou a partida!", result)
        self.assertEqual(len(chess_bot.games), 0)

        with open('tests/support/make_move_legal_move.png', 'rb') as f:
            self.assertEqual(result_board.getvalue(), f.read())

    def test_save_games(self):
        chess_bot = Chess(pickle_filename=PICKLE_FILENAME)
        board1 = chess.Board()
        board1.push_san("e4")
        board1.push_san("e5")
        game1 = Game()
        game1.board = board1
        game1.player1 = FakeDiscordUser(id=1)
        game1.player2 = FakeDiscordUser(id=2)
        board2 = chess.Board()
        board2.push_san("Nf3")
        game2 = Game()
        game2.board = board2
        game2.player1 = 2
        game2.player2 = 3
        chess_bot.games = [game1, game2]

        chess_bot.save_games()

        with open(PICKLE_FILENAME, 'rb') as f:
            self.assertEqual(chess_bot.games, pickle.load(f))

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

        with open("tests/support/get_all_boards_png_one_game.png", 'rb') as f:
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

        with open("tests/support/get_all_boards_png_three_games.png", 'rb') as f:
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

        with open("tests/support/get_all_boards_png_twelve_games.png", 'rb') as f:
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

        image_bytesio = asyncio.run(chess_bot.get_all_boards_png(page=1), debug=True)

        with open("tests/support/get_all_boards_png_twelve_games_second_page.png", 'rb') as f:
            self.assertEqual(image_bytesio.read(), f.read())
    
    def test_get_all_boards_png_no_games_being_played(self):
        chess_bot = Chess()

        image_bytesio = asyncio.run(chess_bot.get_all_boards_png())
        
        self.assertIsNone(image_bytesio)

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
