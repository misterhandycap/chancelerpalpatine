import asyncio
import os
from unittest import TestCase

from dotenv import load_dotenv

from bot.astrology.astrology_chart import AstrologyChart
from bot.social.profile import Profile
from tests.factories.chess_game_factory import ChessGameFactory
from tests.factories.profile_item_factory import ProfileItemFactory
from tests.factories.user_factory import UserFactory
from tests.factories.user_profile_item_factory import UserProfileItemFactory
from tests.factories.xp_point_factory import XpPointFactory
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
        user_1 = UserFactory(name='My very long name')
        user_2 = UserFactory()
        chess_game_1 = ChessGameFactory(player1=user_1, result=1)
        xp_point_1 = XpPointFactory(user=user_1, points=140)
        self.test_session.commit()
        astrology_bot = AstrologyChart()
        datetime = ('1997/08/10', '07:17', '-03:00')
        geopos = (-23.5506507, -46.6333824)
        chart = astrology_bot.calc_chart_raw(datetime, geopos)
        asyncio.run(astrology_bot.save_chart(user_1.id, chart))
        with open(os.path.join('tests', 'support', 'user_avatar.png'), 'rb') as f:
            user_avatar_bytes = f.read()

        result = asyncio.run(Profile().get_user_profile(user_1.id, user_avatar_bytes, lang='pt'))

        with open(os.path.join('tests', 'support', 'get_user_profile_all_fields.png'), 'rb') as f:
            self.assertEqual(result.getvalue(), f.read())

    def test_get_user_profile_user_has_badges(self):
        user_1 = UserFactory(name='Name')
        profile_badge_1 = ProfileItemFactory(
            file_path=os.path.join("tests", "support", "badge1.png")
        )
        profile_badge_2 = ProfileItemFactory(
            file_path=os.path.join("tests", "support", "badge2.png")
        )
        profile_badge_3 = ProfileItemFactory(
            file_path=os.path.join("tests", "support", "badge3.png")
        )
        profile_badge_4 = ProfileItemFactory(
            file_path=os.path.join("tests", "support", "badge1.png")
        )
        user_1.profile_items = [
            UserProfileItemFactory(profile_item=profile_badge_1),
            UserProfileItemFactory(profile_item=profile_badge_2),
            UserProfileItemFactory(profile_item=profile_badge_3),
            UserProfileItemFactory(profile_item=profile_badge_4, equipped=False),
        ]
        self.test_session.commit()
        with open(os.path.join('tests', 'support', 'user_avatar.png'), 'rb') as f:
            user_avatar_bytes = f.read()

        result = asyncio.run(Profile().get_user_profile(user_1.id, user_avatar_bytes, lang='pt'))

        with open(os.path.join('tests', 'support', 'get_user_profile_with_badges.png'), 'rb') as f:
            self.assertEqual(result.getvalue(), f.read())

    def test_get_user_profile_user_has_wallpaper(self):
        user_1 = UserFactory(name='Name')
        profile_badge = ProfileItemFactory(
            type='wallpaper',
            file_path=os.path.join("tests", "support", "wallpaper.png")
        )
        user_1.profile_items = [
            UserProfileItemFactory(profile_item=profile_badge),
        ]
        self.test_session.commit()
        with open(os.path.join('tests', 'support', 'user_avatar.png'), 'rb') as f:
            user_avatar_bytes = f.read()

        result = asyncio.run(Profile().get_user_profile(user_1.id, user_avatar_bytes, lang='pt'))

        with open(os.path.join('tests', 'support', 'get_user_profile_with_wallpaper.png'), 'rb') as f:
            self.assertEqual(result.getvalue(), f.read())

    def test_get_user_profile_user_exists_no_info(self):
        user_1 = UserFactory(name='Name')
        self.test_session.commit()
        with open(os.path.join('tests', 'support', 'user_avatar.png'), 'rb') as f:
            user_avatar_bytes = f.read()

        result = asyncio.run(Profile().get_user_profile(user_1.id, user_avatar_bytes, lang='pt'))

        with open(os.path.join('tests', 'support', 'get_user_profile_no_info.png'), 'rb') as f:
            self.assertEqual(result.getvalue(), f.read())

    def test_get_user_profile_no_user(self):
        with open(os.path.join('tests', 'support', 'user_avatar.png'), 'rb') as f:
            user_avatar_bytes = f.read()

        result = asyncio.run(Profile().get_user_profile(14, user_avatar_bytes, lang='pt'))

        self.assertIsNone(result)
