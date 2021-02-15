import asyncio
import os
from unittest import TestCase

from dotenv import load_dotenv

from bot.astrology.astrology_chart import AstrologyChart
from bot.social.profile import Profile
from bot.models.chess_game import ChessGame
from bot.models.profile_item import ProfileItem
from bot.models.user import User
from bot.models.xp_point import XpPoint
from tests.support.db_connection import clear_data, Session


class TestProfile(TestCase):
    @classmethod
    def setUpClass(cls):
        load_dotenv()
    
    def setUp(self):
        self.test_session = Session()
    
    def tearDown(self):
        clear_data(self.test_session)
        self.test_session.close()

    def test_get_user_profile_all_available_fields(self):
        user_1 = User(id=14, name='My very long name')
        user_2 = User(id=15, name='Them')
        chess_game_1 = ChessGame()
        chess_game_1.player1 = user_1
        chess_game_1.player2 = user_2
        chess_game_1.result = 1
        self.test_session.add(chess_game_1)
        xp_point_1 = XpPoint()
        xp_point_1.user = user_1
        xp_point_1.server_id = 10
        xp_point_1.points = 140
        self.test_session.add(xp_point_1)
        self.test_session.commit()
        astrology_bot = AstrologyChart()
        datetime = ('1997/08/10', '07:17', '-03:00')
        geopos = (-23.5506507, -46.6333824)
        chart = astrology_bot.calc_chart_raw(datetime, geopos)
        asyncio.run(astrology_bot.save_chart(user_1.id, chart))
        with open(os.path.join('tests', 'support', 'user_avatar.png'), 'rb') as f:
            user_avatar_bytes = f.read()

        result = asyncio.run(Profile().get_user_profile(user_1.id, user_avatar_bytes))

        with open(os.path.join('tests', 'support', 'get_user_profile_all_fields.png'), 'rb') as f:
            self.assertEqual(result.getvalue(), f.read())

    def test_get_user_profile_user_has_badges(self):
        user_1 = User(id=14, name='Name')
        profile_badge_1 = ProfileItem()
        profile_badge_1.name = "Item1"
        profile_badge_1.price = 100
        profile_badge_1.type = "badge"
        profile_badge_1.file_path = os.path.join("tests", "support", "badge1.png")
        profile_badge_2 = ProfileItem()
        profile_badge_2.name = "Item2"
        profile_badge_2.price = 100
        profile_badge_2.type = "badge"
        profile_badge_2.file_path = os.path.join("tests", "support", "badge2.png")
        user_1.profile_items = [profile_badge_1, profile_badge_2]
        self.test_session.add(user_1)
        self.test_session.commit()
        with open(os.path.join('tests', 'support', 'user_avatar.png'), 'rb') as f:
            user_avatar_bytes = f.read()

        result = asyncio.run(Profile().get_user_profile(user_1.id, user_avatar_bytes))

        with open(os.path.join('tests', 'support', 'get_user_profile_with_badges.png'), 'rb') as f:
            self.assertEqual(result.getvalue(), f.read())

    def test_get_user_profile_user_exists_no_info(self):
        user_1 = User(id=14, name='Name')
        self.test_session.add(user_1)
        self.test_session.commit()
        with open(os.path.join('tests', 'support', 'user_avatar.png'), 'rb') as f:
            user_avatar_bytes = f.read()

        result = asyncio.run(Profile().get_user_profile(user_1.id, user_avatar_bytes))

        with open(os.path.join('tests', 'support', 'get_user_profile_no_info.png'), 'rb') as f:
            self.assertEqual(result.getvalue(), f.read())

    def test_get_user_profile_no_user(self):
        with open(os.path.join('tests', 'support', 'user_avatar.png'), 'rb') as f:
            user_avatar_bytes = f.read()

        result = asyncio.run(Profile().get_user_profile(14, user_avatar_bytes))

        self.assertIsNone(result)
