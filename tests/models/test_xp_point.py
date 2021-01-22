import asyncio
from unittest import TestCase

from dotenv import load_dotenv

from bot.models.user import User
from bot.models.xp_point import XpPoint
from tests.support.db_connection import clear_data, Session


class TestXpPoint(TestCase):
    @classmethod
    def setUpClass(cls):
        load_dotenv()
    
    def tearDown(self):
        clear_data(Session())

    def test_get_number_of_victories_many_servers(self):
        test_session = Session()
        user = User(id=14, name='Me')
        xp_point_1 = XpPoint()
        xp_point_1.user = user
        xp_point_1.server_id = 10
        xp_point_1.points = 140
        test_session.add(xp_point_1)
        xp_point_2 = XpPoint()
        xp_point_2.user = user
        xp_point_2.server_id = 12
        xp_point_2.points = 260
        test_session.add(xp_point_2)
        test_session.commit()

        result = asyncio.run(XpPoint.get_user_aggregated_points(user.id))

        self.assertEqual(result, 400)

    def test_get_number_of_victories_no_xp_point(self):
        test_session = Session()
        user = User(id=14, name='Me')
        test_session.add(user)
        test_session.commit()

        result = asyncio.run(XpPoint.get_user_aggregated_points(user.id))

        self.assertIsNone(result)

    def test_get_number_of_victories_no_user(self):
        result = asyncio.run(XpPoint.get_user_aggregated_points(14))

        self.assertIsNone(result)
