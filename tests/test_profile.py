import asyncio
from unittest import TestCase

from dotenv import load_dotenv

from bot.astrology.astrology_chart import AstrologyChart
from bot.social.profile import Profile
from bot.models.chess_game import ChessGame
from bot.models.user import User
from bot.models.xp_point import XpPoint
from tests.support.db_connection import clear_data, Session


class TestProfile(TestCase):
    @classmethod
    def setUpClass(cls):
        load_dotenv()
    
    def tearDown(self):
        clear_data(Session())

    def test_get_user_profile_all_available_fields(self):
        test_session = Session()
        user_1 = User(id=14, name='My very long name')
        user_2 = User(id=15, name='Them')
        chess_game_1 = ChessGame()
        chess_game_1.player1 = user_1
        chess_game_1.player2 = user_2
        chess_game_1.result = 1
        test_session.add(chess_game_1)
        xp_point_1 = XpPoint()
        xp_point_1.user = user_1
        xp_point_1.server_id = 10
        xp_point_1.points = 140
        test_session.add(xp_point_1)
        test_session.commit()
        astrology_bot = AstrologyChart()
        datetime = ('1997/08/10', '07:17', '-03:00')
        geopos = (-23.5506507, -46.6333824)
        chart = astrology_bot.calc_chart_raw(datetime, geopos)
        asyncio.run(astrology_bot.save_chart(user_1.id, chart))
        with open('tests/support/user_avatar.png', 'rb') as f:
            user_avatar_bytes = f.read()

        result = asyncio.run(Profile().get_user_profile(user_1.id, user_avatar_bytes))

        with open('tests/support/get_user_profile_all_fields.png', 'rb') as f:
            self.assertEqual(result.getvalue(), f.read())

    def test_get_user_profile_user_exists_no_info(self):
        test_session = Session()
        user_1 = User(id=14, name='Name')
        test_session.add(user_1)
        test_session.commit()
        with open('tests/support/user_avatar.png', 'rb') as f:
            user_avatar_bytes = f.read()

        result = asyncio.run(Profile().get_user_profile(user_1.id, user_avatar_bytes))

        with open('tests/support/get_user_profile_no_info.png', 'rb') as f:
            self.assertEqual(result.getvalue(), f.read())

    def test_get_user_profile_no_user(self):
        with open('tests/support/user_avatar.png', 'rb') as f:
            user_avatar_bytes = f.read()

        result = asyncio.run(Profile().get_user_profile(14, user_avatar_bytes))

        self.assertIsNone(result)
