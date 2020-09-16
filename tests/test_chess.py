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

    def test_make_move_finish_game(self):
        board = chess.Board()
        board.push_san("g4")
        board.push_san("e5")
        board.push_san("f4")
        game = Game()
        game.board = board
        game.player1 = 1
        game.player2 = 2
        game.current_player = game.player1

        chess_bot = Chess()
        chess_bot.games.append(game)
        result, result_board = chess_bot.make_move(game.player1, 'd8h4')

        self.assertIn("Game over", result)
        self.assertIsNotNone(result_board)
        self.assertEqual(len(chess_bot.games), 0)

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

    def test_make_move_mutiple_games_with_given_player2(self):
        board1 = chess.Board()
        board1.push_san("e4")
        board1.push_san("e5")
        game1 = Game()
        game1.board = board1
        game1.player1 = 1
        game1.player2 = 2
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
        result, result_board = chess_bot.make_move(game1.player1, 'g1f3', other_player=game1.player2)

        self.assertIn("It's your turn", result)
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
        game1.player1 = 1
        game1.player2 = 2
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

        self.assertIn("playing 2 games", result)
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
        game1.player1 = 1
        game1.player2 = 2
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
        result, result_board = chess_bot.make_move(game1.player1, 'g1f3', other_player=14)

        self.assertIn("Game not found", result)
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
        game.player1 = 1
        game.player2 = 2
        game.current_player = game.player1

        chess_bot = Chess()
        chess_bot.games.append(game)
        result, result_board = chess_bot.resign(game.player1)

        self.assertIn("resign the game!", result)
        self.assertIsNotNone(result_board)
        self.assertEqual(len(chess_bot.games), 0)

    def test_resign_game_not_found(self):
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
        result, result_board = chess_bot.resign(game.player2)

        self.assertIn("it is not your move", result)
        self.assertIsNone(result_board)
        self.assertEqual(len(chess_bot.games), 1)

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
