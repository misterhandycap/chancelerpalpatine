import asyncio
import os
from datetime import datetime, timedelta
from unittest import TestCase

from dotenv import load_dotenv

from bot.economy.exceptions import AlreadyOwnsItem, ItemNotFound, NotEnoughCredits
from bot.economy.palplatina import Palplatina
from bot.models.user import User
from bot.models.user_profile_item import UserProfileItem
from tests.factories.profile_item_factory import ProfileItemFactory
from tests.factories.user_factory import UserFactory
from tests.factories.user_profile_item_factory import UserProfileItemFactory
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
        Session.remove()
    
    def test_give_daily_clear_for_new_daily(self):
        user = UserFactory(
            currency=150,
            daily_last_collected_at=datetime.utcnow() - timedelta(days=1)
        )
        self.db_session.commit()

        result, user_actual = asyncio.run(Palplatina().give_daily(user.id, user.name))
        Session.remove()

        self.assertTrue(result)
        self.assertEqual(user_actual.currency, 450)
        self.assertEqual(self.db_session.query(User).get(user.id).currency, 450)

    def test_give_daily_new_user(self):
        result, user = asyncio.run(Palplatina().give_daily(14, "name"))

        self.assertTrue(result)
        self.assertEqual(user.currency, 300)
        self.assertEqual(user.name, "name")
        self.assertEqual(Session().query(User).get(14).currency, 300)

    def test_give_daily_not_clear_for_new_daily(self):
        user = UserFactory(
            currency=150,
            daily_last_collected_at=datetime.utcnow()
        )
        self.db_session.commit()

        result, user_actual = asyncio.run(Palplatina().give_daily(user.id, user.name))
        Session.remove()

        self.assertFalse(result)
        self.assertEqual(user_actual.currency, 150)
        self.assertEqual(self.db_session.query(User).get(user.id).currency, 150)

    def test_get_currency_user_exists(self):
        user = UserFactory(currency=150)
        self.db_session.commit()

        result = asyncio.run(Palplatina().get_currency(user.id))

        self.assertEqual(result, 150)

    def test_get_currency_user_doesnt_exist(self):
        result = asyncio.run(Palplatina().get_currency(14))

        self.assertEqual(result, 0)

    def test_buy_item_success(self):
        user = UserFactory(currency=150)
        profile_item = ProfileItemFactory(price=100)
        self.db_session.commit()

        result = asyncio.run(Palplatina().buy_item(user.id, profile_item.name))
        Session.remove()

        self.assertIsInstance(result, User)
        self.assertEqual(result.currency, 50)
        self.assertEqual(result.profile_items[0].profile_item.id, profile_item.id)

        persisted_user = self.db_session.query(User).get(user.id)
        persisted_user_profile_items = persisted_user.profile_items
        self.assertEqual(persisted_user.currency, 50)
        self.assertEqual(len(persisted_user_profile_items), 1)
        self.assertEqual(persisted_user_profile_items[0].profile_item.id, profile_item.id)

    def test_buy_item_not_enough_currency(self):
        user = UserFactory(currency=150)
        profile_item = ProfileItemFactory(price=200)
        self.db_session.commit()

        with self.assertRaises(NotEnoughCredits):
            asyncio.run(Palplatina().buy_item(user.id, profile_item.name))

        Session.remove()
        persisted_user = self.db_session.query(User).get(user.id)
        persisted_user_profile_items = persisted_user.profile_items
        self.assertEqual(persisted_user.currency, 150)
        self.assertEqual(len(persisted_user_profile_items), 0)

    def test_buy_item_item_already_bought(self):
        profile_item = ProfileItemFactory()
        user = UserFactory(currency=150)
        user.profile_items = [UserProfileItemFactory(profile_item=profile_item)]
        self.db_session.commit()

        with self.assertRaises(AlreadyOwnsItem):
            asyncio.run(Palplatina().buy_item(user.id, profile_item.name))

        persisted_user = self.db_session.query(User).get(user.id)
        persisted_user_profile_items = persisted_user.profile_items
        self.assertEqual(persisted_user.currency, 150)
        self.assertEqual(len(persisted_user_profile_items), 1)
        self.assertEqual(persisted_user_profile_items[0].profile_item.id, profile_item.id)

    def test_buy_item_item_not_found(self):
        user = UserFactory(currency=150)
        self.db_session.commit()

        with self.assertRaises(ItemNotFound):
            asyncio.run(Palplatina().buy_item(user.id, 'random'))

        Session.remove()
        persisted_user = self.db_session.query(User).get(user.id)
        persisted_user_profile_items = persisted_user.profile_items
        self.assertEqual(persisted_user.currency, 150)
        self.assertEqual(len(persisted_user_profile_items), 0)

    def test_buy_item_user_not_found(self):
        with self.assertRaises(ItemNotFound):
            asyncio.run(Palplatina().buy_item(14, 'random'))

    def test_get_available_items(self):
        ProfileItemFactory.reset_sequence()
        for i in range(12):
            ProfileItemFactory()
        self.db_session.commit()

        result = asyncio.run(Palplatina().get_available_items(page=0))

        self.assertEqual(len(result), 2)
        self.assertEqual(len(result[0]), 9)
        self.assertEqual(result[1], 2)
        fetched_items_names = [item.name for item in result[0]]
        self.assertIn('Profile item 0', fetched_items_names)
        self.assertIn('Profile item 8', fetched_items_names)
        self.assertNotIn('Profile item 9', fetched_items_names)
        self.assertNotIn('Profile item 11', fetched_items_names)

    def test_get_user_items_user_has_items(self):
        user = UserFactory()
        ProfileItemFactory.reset_sequence()
        for i in range(2):
            profile_item = ProfileItemFactory()
            user.profile_items.append(UserProfileItemFactory(profile_item=profile_item))
        another_profile_item = ProfileItemFactory()
        self.db_session.commit()

        result = asyncio.run(Palplatina().get_user_items(user.id))

        self.assertEqual(len(result), 2)
        fetched_items_names = [item.profile_item.name for item in result]
        self.assertIn('Profile item 0', fetched_items_names)
        self.assertIn('Profile item 1', fetched_items_names)
        self.assertNotIn(another_profile_item.name, fetched_items_names)

    def test_get_user_items_user_has_no_items(self):
        user = UserFactory()
        self.db_session.commit()

        result = asyncio.run(Palplatina().get_user_items(user.id))

        self.assertEqual(len(result), 0)

    def test_get_user_items_user_not_found(self):
        result = asyncio.run(Palplatina().get_user_items(14))

        self.assertEqual(len(result), 0)

    def test_get_item_item_exists(self):
        profile_item = ProfileItemFactory()
        self.db_session.commit()

        result = asyncio.run(Palplatina().get_item(profile_item.name))

        self.assertEqual(result.id, profile_item.id)

    def test_get_item_item_does_not_exist(self):
        result = asyncio.run(Palplatina().get_item("item"))

        self.assertIsNone(result)

    def test_equip_item_user_has_item(self):
        user = UserFactory()
        profile_item = ProfileItemFactory()
        user.profile_items = [UserProfileItemFactory(
            equipped=False, profile_item=profile_item)]
        self.db_session.commit()

        result = asyncio.run(Palplatina().equip_item(user.id, profile_item.name))

        self.assertTrue(result.equipped)
        
        Session.remove()
        fetched_user_profile_item = self.db_session.query(UserProfileItem).get((user.id, profile_item.id))
        self.assertTrue(fetched_user_profile_item.equipped)

    def test_equip_item_user_does_not_have_item(self):
        user = UserFactory()
        self.db_session.commit()

        with self.assertRaises(ItemNotFound):
            asyncio.run(Palplatina().equip_item(user.id, 'some item'))


    def test_equip_item_user_does_not_exist(self):
        with self.assertRaises(ItemNotFound):
            asyncio.run(Palplatina().equip_item(140, 'some item'))

    def test_unequip_item_user_has_item(self):
        user = UserFactory()
        profile_item = ProfileItemFactory()
        user.profile_items = [UserProfileItemFactory(
            equipped=True, profile_item=profile_item)]
        self.db_session.commit()

        result = asyncio.run(Palplatina().unequip_item(user.id, profile_item.name))

        self.assertFalse(result.equipped)
        
        Session.remove()
        fetched_user_profile_item = self.db_session.query(UserProfileItem).get((user.id, profile_item.id))
        self.assertFalse(fetched_user_profile_item.equipped)

    def test_unequip_item_user_does_not_have_item(self):
        user = UserFactory()
        self.db_session.commit()

        with self.assertRaises(ItemNotFound):
            asyncio.run(Palplatina().unequip_item(user.id, 'some item'))


    def test_unequip_item_user_does_not_exist(self):
        with self.assertRaises(ItemNotFound):
            asyncio.run(Palplatina().unequip_item(140, 'some item'))
