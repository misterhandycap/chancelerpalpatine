from unittest import TestCase

from dotenv import load_dotenv

from bot.models.exceptions import ProfileItemException
from bot.models.profile_item import ProfileItem, ProfileItemType
from tests.support.db_connection import clear_data, Session


class TestProfileItem(TestCase):
    @classmethod
    def setUpClass(cls):
        load_dotenv()
    
    def tearDown(self):
        clear_data(Session())

    def test_validate_type_valid_type(self):
        profile_item = ProfileItem()
        profile_item.type = 'badge'

    def test_validate_type_invalid_type(self):
        profile_item = ProfileItem()
        with self.assertRaises(ProfileItemException):
            profile_item.type = 'invalid'

    def test_validate_price_valid_price(self):
        profile_item = ProfileItem()
        profile_item.price = 100

    def test_validate_price_invalid_price(self):
        profile_item = ProfileItem()
        with self.assertRaises(ProfileItemException):
            profile_item.price = 'invalid'
        with self.assertRaises(ProfileItemException):
            profile_item.price = -100
