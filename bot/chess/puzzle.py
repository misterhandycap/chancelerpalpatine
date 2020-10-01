import json
from json.decoder import JSONDecodeError

import urllib.request
from chess import Board
from urllib.request import Request
from urllib.error import HTTPError

from bot.chess.game import Game


class Puzzle():

    def __init__(self):
        self.puzzles = {}
    
    def get_random_puzzle(self):
        params = json.dumps({"type": "explore"}).encode('utf-8')
        request = Request("https://chessblunders.org/api/blunder/get", data=params)
        request.add_header("Content-Type", "application/json")
        request.add_header("User-Agent", "HTTPie/1.0.3")
        try:
            response = urllib.request.urlopen(request)
            response_str = response.read().decode('utf-8')

            return json.loads(response_str)
        except JSONDecodeError:
            return {"error": "Invalid JSON", "body": response_str}
        except HTTPError as e:
            return {"error": e.msg, "http_code": e.code}

    def build_puzzle(self, puzzle_dict):
        try:
            puzzle_id = puzzle_dict["data"]["id"]
            first_move = puzzle_dict["data"]["blunderMove"]
            fen = puzzle_dict["data"]["fenBefore"]
            correct_sequence = puzzle_dict["data"]["forcedLine"]

            board = Board(fen)
            board.push_san(first_move)
            game = Game()
            game.board = board
            game.color_schema = "default"
            self.puzzles[puzzle_id] = {
                "id": puzzle_id,
                "game": game,
                "correct_sequence": correct_sequence
            }
            return self.puzzles[puzzle_id]
        except KeyError:
            return {"error": "Missing required keys"}
        except:
            return {"error": "Invalid FEN or move"}

    def validate_puzzle_move(self, puzzle_id, move):
        try:
            puzzle = self.puzzles[puzzle_id]
            expected_move_san_str = puzzle["correct_sequence"][0]
            expected_move = puzzle["game"].board.parse_san(expected_move_san_str)

            result = move == expected_move_san_str or move == expected_move.uci()
            if result and len(puzzle["correct_sequence"]) > 1:
                puzzle["game"].board.push_san(puzzle["correct_sequence"].pop(0))
                puzzle["game"].board.push_san(puzzle["correct_sequence"].pop(0))
            
            return result
        except KeyError:
            return "Puzzle not found"

    def is_puzzle_over(self, puzzle_id):
        try:
            puzzle = self.puzzles[puzzle_id]
            return len(puzzle["correct_sequence"]) <= 1
        except KeyError:
            return "Puzzle not found"

