import os
import pickle
from unittest import TestCase

import chess

from bot.chess import Chess, Game


PICKLE_FILENAME = 'games_test.pickle'


class TestChess(TestCase):

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
        game1.player1 = 1
        game1.player2 = 2
        board2 = chess.Board()
        board2.push_san("Nf3")
        game2 = Game()
        game2.board = board2
        game2.player1 = 2
        game2.player2 = 3
        games = [game1, game2]

        with open(PICKLE_FILENAME, 'wb') as f:
            pickle.dump(games, f)

        chess_bot = Chess(pickle_filename=PICKLE_FILENAME)
        self.assertEqual(games, chess_bot.load_games())

    def test_load_games_file_doesnt_exist(self):
        self.assertEqual([], Chess().load_games())

    def test_new_game_new_players(self):
        player1 = 1
        player2 = 2

        chess_bot = Chess()
        result = chess_bot.new_game(player1, player2)
        games = chess_bot.games

        self.assertIn('Game started', result)
        self.assertEqual(len(games), 1)
        self.assertEqual(games[0].player1, player1)
        self.assertEqual(games[0].player2, player2)
        self.assertEqual(games[0].board.move_stack, [])

    def test_new_game_game_already_started(self):
        game = Game()
        game.player1 = 1
        game.player2 = 2
        
        chess_bot = Chess()
        chess_bot.games.append(game)

        result = chess_bot.new_game(game.player1, game.player2)
        self.assertIn('Game already in progress', result)
        self.assertEqual(len(chess_bot.games), 1)

    def test_make_move_legal_move_in_players_turn(self):
        board = chess.Board()
        board.push_san("e4")
        board.push_san("e5")
        game = Game()
        game.board = board
        game.player1 = 1
        game.player2 = 2
        game.current_player = game.player1

        chess_bot = Chess()
        chess_bot.games.append(game)
        result, result_board = chess_bot.make_move(game.player1, 'g1f3')

        self.assertIn("It's your turn", result)
        self.assertIsNotNone(result_board)
        self.assertEqual(len(game.board.move_stack), 3)
        self.assertEqual(game.current_player, game.player2)

    def test_make_move_illegal_move_in_players_turn(self):
        board = chess.Board()
        board.push_san("e4")
        board.push_san("e5")
        game = Game()
        game.board = board
        game.player1 = 1
        game.player2 = 2
        game.current_player = game.player1

        chess_bot = Chess()
        chess_bot.games.append(game)
        result, result_board = chess_bot.make_move(game.player1, 'invalid')

        self.assertIn("Invalid move", result)
        self.assertIsNone(result_board)
        self.assertEqual(len(game.board.move_stack), 2)
        self.assertEqual(game.current_player, game.player1)

    def test_make_move_move_not_in_players_turn(self):
        board = chess.Board()
        board.push_san("e4")
        board.push_san("e5")
        game = Game()
        game.board = board
        game.player1 = 1
        game.player2 = 2
        game.current_player = game.player1

        chess_bot = Chess()
        chess_bot.games.append(game)
        result, result_board = chess_bot.make_move(game.player2, 'g1f3')

        self.assertIn("it is not your move", result)
        self.assertIsNone(result_board)
        self.assertEqual(len(game.board.move_stack), 2)
        self.assertEqual(game.current_player, game.player1)

    def test_save_games(self):
        chess_bot = Chess(pickle_filename=PICKLE_FILENAME)
        board1 = chess.Board()
        board1.push_san("e4")
        board1.push_san("e5")
        game1 = Game()
        game1.board = board1
        game1.player1 = 1
        game1.player2 = 2
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
