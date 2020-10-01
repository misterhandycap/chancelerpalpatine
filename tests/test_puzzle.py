from unittest import TestCase

from chess import Board

from bot.chess.game import Game
from bot.chess.puzzle import Puzzle


class TestPuzzle(TestCase):

    def test_get_puzzle(self):
        puzzle_bot = Puzzle()

        actual = puzzle_bot.get_random_puzzle()

        self.assertIn("data", actual)
        self.assertIn("blunderMove", actual["data"])
        self.assertIn("fenBefore", actual["data"])
        self.assertIn("forcedLine", actual["data"])
        self.assertIn("id", actual["data"])

    def test_validate_move_correct_san_move(self):
        puzzle_bot, puzzle_id = self._build_puzzle_bot_with_one_puzzle()

        result = puzzle_bot.validate_puzzle_move(puzzle_id, "Kg5")

        self.assertTrue(result)

    def test_validate_move_correct_uci_move(self):
        puzzle_bot, puzzle_id = self._build_puzzle_bot_with_one_puzzle()

        result = puzzle_bot.validate_puzzle_move(puzzle_id, "h5g5")

        self.assertTrue(result)

    def test_validate_move_incorrect_san_move(self):
        puzzle_bot, puzzle_id = self._build_puzzle_bot_with_one_puzzle()

        result = puzzle_bot.validate_puzzle_move(puzzle_id, "Kh6")

        self.assertFalse(result)

    def test_validate_move_incorrect_uci_move(self):
        puzzle_bot, puzzle_id = self._build_puzzle_bot_with_one_puzzle()

        result = puzzle_bot.validate_puzzle_move(puzzle_id, "h5h6")

        self.assertFalse(result)

    def test_validate_move_invalid_move(self):
        puzzle_bot, puzzle_id = self._build_puzzle_bot_with_one_puzzle()

        result = puzzle_bot.validate_puzzle_move(puzzle_id, "invalid")

        self.assertFalse(result)

    def test_is_puzzle_over_new_puzzle(self):
        puzzle_bot, puzzle_id = self._build_puzzle_bot_with_one_puzzle()

        result = puzzle_bot.is_puzzle_over(puzzle_id)

        self.assertFalse(result)

    def test_is_puzzle_over_ongoing_puzzle(self):
        puzzle_bot, puzzle_id = self._build_puzzle_bot_with_one_puzzle()
        puzzle_bot.validate_puzzle_move(puzzle_id, "Kg5")

        result = puzzle_bot.is_puzzle_over(puzzle_id)

        self.assertFalse(result)

    def test_is_puzzle_over_ended_puzzle(self):
        puzzle_bot, puzzle_id = self._build_puzzle_bot_with_one_puzzle()
        puzzle_bot.validate_puzzle_move(puzzle_id, "Kg5")
        puzzle_bot.validate_puzzle_move(puzzle_id, "Qxf1+")
        puzzle_bot.validate_puzzle_move(puzzle_id, "Qf4+")

        result = puzzle_bot.is_puzzle_over(puzzle_id)

        self.assertTrue(result)

    def _build_puzzle_bot_with_one_puzzle(self):
        puzzle_bot = Puzzle()
        game = Game()
        game.board = Board("8/7p/4p1p1/1p5k/8/PB4PK/2P2q1P/4R3 w - - 0 37")
        game.board.push_san("g4+")
        puzzle_id = "557ca53de13823b83a98100e"
        puzzle_bot.puzzles = {
            puzzle_id: {
                "game": game,
                "correct_sequence": [
                    "Kg5",
                    "Rf1",
                    "Qxf1+",
                    "Kg3",
                    "Qf4+"
                ]
            }
        }
        return puzzle_bot, puzzle_id
