import asyncio
import os
from datetime import datetime, timedelta
from unittest import TestCase

from dotenv import load_dotenv

from bot.economy.exceptions import AlreadyOwnsItem, ItemNotFound, NotEnoughCredits
from bot.economy.palplatina import Palplatina
from bot.models.profile_item import ProfileItem
from bot.models.user import User
from tests.support.db_connection import clear_data, Session


class TestPalplatina(TestCase):

    @classmethod
    def setUpClass(cls):
        load_dotenv()
    
    def setUp(self):
        self.db_session = Session()
    
    def tearDown(self):
        clear_data(self.db_session)
        self.db_session.close()
    
    def test_give_daily_clear_for_new_daily(self):
        user = User()
        user.id = 14
        user.daily_last_collected_at = datetime.utcnow() - timedelta(days=1)
        user.currency = 150
        self.db_session.add(user)
        self.db_session.commit()

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
        user = User()
        user.id = 14
        user.daily_last_collected_at = datetime.utcnow()
        user.currency = 150
        self.db_session.add(user)
        self.db_session.commit()

        result, user_actual = asyncio.run(Palplatina().give_daily(user.id, user.name))

        self.assertFalse(result)
        self.assertEqual(user_actual.currency, 150)
        self.assertEqual(Session().query(User).get(user.id).currency, 150)

    def test_get_currency_user_exists(self):
        user = User()
        user.id = 14
        user.daily_last_collected_at = datetime.utcnow()
        user.currency = 150
        self.db_session.add(user)
        self.db_session.commit()

        result = asyncio.run(Palplatina().get_currency(user.id))

        self.assertEqual(result, 150)

    def test_get_currency_user_doesnt_exist(self):
        result = asyncio.run(Palplatina().get_currency(14))

        self.assertEqual(result, 0)

    def test_buy_item_success(self):
        user = User()
        user.id = 14
        user.daily_last_collected_at = datetime.utcnow()
        user.currency = 150
        self.db_session.add(user)
        profile_item = ProfileItem()
        profile_item.name = 'Item'
        profile_item.price = 100
        profile_item.type = 'badge'
        profile_item.file_path = os.path.join('some', 'path.png')
        self.db_session.add(profile_item)
        self.db_session.commit()

        result = asyncio.run(Palplatina().buy_item(user.id, profile_item.name))

        self.assertIsInstance(result, User)
        self.assertEqual(result.currency, 50)
        self.assertEqual(result.profile_items[0].id, profile_item.id)

        persisted_user = Session().query(User).get(user.id)
        persisted_user_profile_items = persisted_user.profile_items
        self.assertEqual(persisted_user.currency, 50)
        self.assertEqual(len(persisted_user_profile_items), 1)
        self.assertEqual(persisted_user_profile_items[0].id, profile_item.id)

    def test_buy_item_not_enough_currency(self):
        user = User()
        user.id = 14
        user.daily_last_collected_at = datetime.utcnow()
        user.currency = 150
        self.db_session.add(user)
        profile_item = ProfileItem()
        profile_item.name = 'Item'
        profile_item.price = 200
        profile_item.type = 'badge'
        profile_item.file_path = os.path.join('some', 'path.png')
        self.db_session.add(profile_item)
        self.db_session.commit()

        with self.assertRaises(NotEnoughCredits):
            asyncio.run(Palplatina().buy_item(user.id, profile_item.name))

        persisted_user = Session().query(User).get(user.id)
        persisted_user_profile_items = persisted_user.profile_items
        self.assertEqual(persisted_user.currency, 150)
        self.assertEqual(len(persisted_user_profile_items), 0)

    def test_buy_item_item_already_bought(self):
        profile_item = ProfileItem()
        profile_item.name = 'Item'
        profile_item.price = 100
        profile_item.type = 'badge'
        profile_item.file_path = os.path.join('some', 'path.png')
        self.db_session.add(profile_item)
        user = User()
        user.id = 14
        user.daily_last_collected_at = datetime.utcnow()
        user.currency = 150
        user.profile_items = [profile_item]
        self.db_session.add(user)
        self.db_session.commit()

        with self.assertRaises(AlreadyOwnsItem):
            asyncio.run(Palplatina().buy_item(user.id, profile_item.name))

        persisted_user = Session().query(User).get(user.id)
        persisted_user_profile_items = persisted_user.profile_items
        self.assertEqual(persisted_user.currency, 150)
        self.assertEqual(len(persisted_user_profile_items), 1)
        self.assertEqual(persisted_user_profile_items[0].id, profile_item.id)

    def test_buy_item_item_not_found(self):
        user = User()
        user.id = 14
        user.daily_last_collected_at = datetime.utcnow()
        user.currency = 150
        self.db_session.add(user)
        self.db_session.commit()

        with self.assertRaises(ItemNotFound):
            asyncio.run(Palplatina().buy_item(user.id, 'random'))

        persisted_user = Session().query(User).get(user.id)
        persisted_user_profile_items = persisted_user.profile_items
        self.assertEqual(persisted_user.currency, 150)
        self.assertEqual(len(persisted_user_profile_items), 0)

    def test_buy_item_user_not_found(self):
        with self.assertRaises(ItemNotFound):
            asyncio.run(Palplatina().buy_item(14, 'random'))

    def test_get_available_items(self):
        for i in range(12):
            profile_item = ProfileItem()
            profile_item.name = f'Item{i}'
            profile_item.price = i*25
            profile_item.type = 'badge' if i % 2 else 'wallpaper'
            profile_item.file_path = os.path.join('some', f'path_{i}.png')
            self.db_session.add(profile_item)
        self.db_session.commit()

        result = asyncio.run(Palplatina().get_available_items(page=0))

        self.assertEqual(len(result), 2)
        self.assertEqual(len(result[0]), 9)
        self.assertEqual(result[1], 2)
        fetched_items_names = [item.name for item in result[0]]
        self.assertIn('Item0', fetched_items_names)
        self.assertIn('Item8', fetched_items_names)
        self.assertNotIn('Item9', fetched_items_names)
        self.assertNotIn('Item11', fetched_items_names)

    def test_get_user_items_user_has_items(self):
        user = User()
        user.id = 14
        user.daily_last_collected_at = datetime.utcnow()
        user.currency = 150
        for i in range(2):
            profile_item = ProfileItem()
            profile_item.name = f'Item{i}'
            profile_item.price = 100*i
            profile_item.type = 'badge'
            profile_item.file_path = os.path.join('some', f'path_{i}.png')
            user.profile_items.append(profile_item)
        self.db_session.add(user)
        self.db_session.commit()

        result = asyncio.run(Palplatina().get_user_items(user.id))

        self.assertEqual(len(result), 2)
        fetched_items_names = [item.name for item in result]
        self.assertIn('Item0', fetched_items_names)
        self.assertIn('Item1', fetched_items_names)

    def test_get_user_items_user_has_no_items(self):
        user = User()
        user.id = 14
        user.daily_last_collected_at = datetime.utcnow()
        user.currency = 150
        self.db_session.add(user)
        self.db_session.commit()

        result = asyncio.run(Palplatina().get_user_items(user.id))

        self.assertEqual(len(result), 0)

    def test_get_user_items_user_not_found(self):
        result = asyncio.run(Palplatina().get_user_items(14))

        self.assertEqual(len(result), 0)

    def test_get_item_item_exists(self):
        profile_item = ProfileItem()
        profile_item.name = 'Item'
        profile_item.price = 100
        profile_item.type = 'badge'
        profile_item.file_path = os.path.join('some', 'path.png')
        self.db_session.add(profile_item)
        self.db_session.commit()

        result = asyncio.run(Palplatina().get_item(profile_item.name))

        self.assertEqual(result.id, profile_item.id)

    def test_get_item_item_does_not_exist(self):
        result = asyncio.run(Palplatina().get_item("item"))

        self.assertIsNone(result)
