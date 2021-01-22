import asyncio
from unittest import TestCase

from dotenv import load_dotenv

from bot.models.chess_game import ChessGame
from bot.models.user import User
from tests.support.db_connection import clear_data, Session


class TestChessGame(TestCase):
    @classmethod
    def setUpClass(cls):
        load_dotenv()
    
    def tearDown(self):
        clear_data(Session())

    def test_get_number_of_victories_many_games(self):
        test_session = Session()
        user_1 = User(id=14, name='Me')
        user_2 = User(id=15, name='Them')
        chess_game_1 = ChessGame()
        chess_game_1.player1 = user_1
        chess_game_1.player2 = user_2
        chess_game_1.result = 1
        test_session.add(chess_game_1)
        chess_game_2 = ChessGame()
        chess_game_2.player1 = user_2
        chess_game_2.player2 = user_1
        chess_game_2.result = 1
        test_session.add(chess_game_2)
        chess_game_3 = ChessGame()
        chess_game_3.player1 = user_2
        chess_game_3.player2 = user_1
        chess_game_3.result = -1
        test_session.add(chess_game_3)
        test_session.commit()

        result = asyncio.run(ChessGame.get_number_of_victories(user_1.id))

        self.assertEqual(result, 2)

    def test_get_number_of_victories_no_games(self):
        test_session = Session()
        user_1 = User(id=14, name='Me')
        user_2 = User(id=15, name='Them')
        test_session.add(user_1)
        test_session.commit()

        result = asyncio.run(ChessGame.get_number_of_victories(user_1.id))

        self.assertEqual(result, 0)

    def test_get_number_of_victories_no_user(self):
        result = asyncio.run(ChessGame.get_number_of_victories(14))

        self.assertEqual(result, 0)
