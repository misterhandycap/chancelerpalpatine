import asyncio
from datetime import datetime, timedelta
from unittest import TestCase

from dotenv import load_dotenv

from bot.economy.palplatina import Palplatina
from bot.models.user import User
from tests.support.db_connection import clear_data, Session


class TestPalplatina(TestCase):

    @classmethod
    def setUpClass(cls):
        load_dotenv()
    
    def tearDown(self):
        clear_data(Session())
    
    def test_give_daily_clear_for_new_daily(self):
        db_session = Session()
        user = User()
        user.id = 14
        user.daily_last_collected_at = datetime.utcnow() - timedelta(days=1)
        user.currency = 150
        db_session.add(user)
        db_session.commit()

        result, user_actual = asyncio.run(Palplatina().give_daily(user.id, user.name))

        self.assertTrue(result)
        self.assertEqual(user_actual.currency, 450)
        self.assertEqual(Session().query(User).get(user.id).currency, 450)

    def test_give_daily_new_user(self):
        result, user = asyncio.run(Palplatina().give_daily(14, "name"))

        self.assertTrue(result)
        self.assertEqual(user.currency, 300)
        self.assertEqual(user.name, "name")
        self.assertEqual(Session().query(User).get(14).currency, 300)

    def test_give_daily_not_clear_for_new_daily(self):
        db_session = Session()
        user = User()
        user.id = 14
        user.daily_last_collected_at = datetime.utcnow()
        user.currency = 150
        db_session.add(user)
        db_session.commit()

        result, user_actual = asyncio.run(Palplatina().give_daily(user.id, user.name))

        self.assertFalse(result)
        self.assertEqual(user_actual.currency, 150)
        self.assertEqual(Session().query(User).get(user.id).currency, 150)

    def test_get_currency_user_exists(self):
        db_session = Session()
        user = User()
        user.id = 14
        user.daily_last_collected_at = datetime.utcnow()
        user.currency = 150
        db_session.add(user)
        db_session.commit()

        result = asyncio.run(Palplatina().get_currency(user.id))

        self.assertEqual(result, 150)

    def test_get_currency_user_doesnt_exist(self):
        result = asyncio.run(Palplatina().get_currency(14))

        self.assertEqual(result, 0)
