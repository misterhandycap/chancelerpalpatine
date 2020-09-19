import asyncio
import os
import pickle
from unittest import TestCase

import chess
from dotenv import load_dotenv

from bot.chess import Chess, Game, Player

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
        result, result_board = chess_bot.make_move(game.player1, 'g1f3')

        self.assertIn("Seu turno é agora", result)
        self.assertIsNotNone(result_board)
        self.assertEqual(len(game.board.move_stack), 3)
        self.assertEqual(game.current_player, game.player2)

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
        result, result_board = chess_bot.make_move(game.player1, 'Nf3')

        self.assertIn("Seu turno é agora", result)
        self.assertIsNotNone(result_board)
        self.assertEqual(len(game.board.move_stack), 3)
        self.assertEqual(game.current_player, game.player2)

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
        result, result_board = chess_bot.make_move(game.player1, 'd8h4')

        self.assertIn("Fim de jogo", result)
        self.assertIn("1. g4 e5 2. f4 Qh4# 0-1", result)
        self.assertIsNotNone(result_board)
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
        result, result_board = chess_bot.make_move(game.player1, 'invalid')

        self.assertIn("Movimento inválido", result)
        self.assertIsNone(result_board)
        self.assertEqual(len(game.board.move_stack), 2)
        self.assertEqual(game.current_player, game.player1)

    def test_make_move_move_not_in_players_turn(self):
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
        result, result_board = chess_bot.make_move(game.player2, 'g1f3')

        self.assertIn("não é mais seu turno", result)
        self.assertIsNone(result_board)
        self.assertEqual(len(game.board.move_stack), 2)
        self.assertEqual(game.current_player, game.player1)

    def test_make_move_mutiple_games_with_given_player2(self):
        board1 = chess.Board()
        board1.push_san("e4")
        board1.push_san("e5")
        game1 = Game()
        game1.board = board1
        game1.player1 = FakeDiscordUser(id=1)
        game1.player2 = FakeDiscordUser(id=2)
        game1.current_player = game1.player1

        board2 = chess.Board()
        board2.push_san("Nf3")
        game2 = Game()
        game2.board = board2
        game2.player1 = 3
        game2.player2 = game1.player1
        game2.current_player = game1.player1

        chess_bot = Chess()
        chess_bot.games.append(game1)
        chess_bot.games.append(game2)
        result, result_board = chess_bot.make_move(game1.player1, 'g1f3', other_user=game1.player2)

        self.assertIn("Seu turno é agora", result)
        self.assertIsNotNone(result_board)
        self.assertEqual(len(game1.board.move_stack), 3)
        self.assertEqual(game1.current_player, game1.player2)
        self.assertEqual(len(game2.board.move_stack), 1)
        self.assertEqual(game2.current_player, game1.player1)

    def test_make_move_multiple_games_waiting_for_same_player(self):
        board1 = chess.Board()
        board1.push_san("e4")
        board1.push_san("e5")
        game1 = Game()
        game1.board = board1
        game1.player1 = FakeDiscordUser(id=1)
        game1.player2 = FakeDiscordUser(id=2)
        game1.current_player = game1.player1

        board2 = chess.Board()
        board2.push_san("Nf3")
        game2 = Game()
        game2.board = board2
        game2.player1 = 3
        game2.player2 = game1.player1
        game2.current_player = game1.player1

        chess_bot = Chess()
        chess_bot.games.append(game1)
        chess_bot.games.append(game2)
        result, result_board = chess_bot.make_move(game1.player1, 'g1f3')

        self.assertIn("jogando 2 partidas", result)
        self.assertIsNone(result_board)
        self.assertEqual(len(game1.board.move_stack), 2)
        self.assertEqual(game1.current_player, game1.player1)
        self.assertEqual(len(game2.board.move_stack), 1)
        self.assertEqual(game2.current_player, game1.player1)

    def test_make_move_multiple_games_with_invalid_player2(self):
        board1 = chess.Board()
        board1.push_san("e4")
        board1.push_san("e5")
        game1 = Game()
        game1.board = board1
        game1.player1 = FakeDiscordUser(id=1)
        game1.player2 = FakeDiscordUser(id=2)
        game1.current_player = game1.player1

        board2 = chess.Board()
        board2.push_san("Nf3")
        game2 = Game()
        game2.board = board2
        game2.player1 = FakeDiscordUser(id=3)
        game2.player2 = game1.player1
        game2.current_player = game1.player1

        chess_bot = Chess()
        chess_bot.games.append(game1)
        chess_bot.games.append(game2)
        result, result_board = chess_bot.make_move(game1.player1, 'g1f3', other_user=FakeDiscordUser(id=14))

        self.assertIn("Partida não encontrada", result)
        self.assertIsNone(result_board)
        self.assertEqual(len(game1.board.move_stack), 2)
        self.assertEqual(game1.current_player, game1.player1)
        self.assertEqual(len(game2.board.move_stack), 1)
        self.assertEqual(game2.current_player, game1.player1)

    def test_resign_game_found(self):
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
        result, result_board = chess_bot.resign(game.player1)

        self.assertIn("abandonou a partida!", result)
        self.assertIsNotNone(result_board)
        self.assertEqual(len(chess_bot.games), 0)

    def test_resign_game_not_found(self):
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
        result, result_board = chess_bot.resign(game.player2)

        self.assertIn("não é mais seu turno", result)
        self.assertIsNone(result_board)
        self.assertEqual(len(chess_bot.games), 1)

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
        result = chess_bot.generate_pgn(user=FakeDiscordUser(id=1))

        self.assertIn('[White "Player1"]', result)
        self.assertIn('[Black "Player2"]', result)
        self.assertIn('1. g4 e5 2. f4 *', result)

    def test_get_all_boards_png(self):
        chess_bot = Chess()

        board1 = chess.Board()
        board1.push_san("e4")
        board1.push_san("e5")
        game1 = Game()
        game1.board = board1
        chess_bot.games.append(game1)

        board2 = chess.Board()
        board2.push_san("Nf3")
        board2.push_san("d6")
        game2 = Game()
        game2.board = board2
        chess_bot.games.append(game2)

        board3 = chess.Board()
        board3.push_san("Nf3")
        game3 = Game()
        game3.board = board3
        chess_bot.games.append(game3)
        
        image_bytesio = chess_bot.get_all_boards_png()
        self.assertGreater(len(image_bytesio.read()), 0)

    def test_is_last_move_blunder_true(self):
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
        result = asyncio.run(chess_bot.is_last_move_blunder(game.player1))

        self.assertTrue(result)
    
    def test_is_last_move_blunder_false(self):
        board = chess.Board()
        board.push_san("g4")
        board.push_san("e5")
        board.push_san("f4")
        game = Game()
        game.board = board
        game.player1 = FakeDiscordUser(id=1)
        game.player2 = FakeDiscordUser(id=2)
        game.current_player = game.player1
        game.last_eval = -100000

        chess_bot = Chess()
        chess_bot.games.append(game)
        result = asyncio.run(chess_bot.is_last_move_blunder(game.player1))

        self.assertFalse(result)


class FakeDiscordUser():

    def __init__(self, id=None, name=None):
        self.id = id
        self.name = name

    def __eq__(self, value):
        try:
            return self.id == value.id
        except:
            return False
