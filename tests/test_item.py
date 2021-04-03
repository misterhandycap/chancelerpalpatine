import asyncio
import os
from unittest import TestCase

from dotenv import load_dotenv

from bot.economy.item import Item
from bot.models.profile_item import ProfileItem
from tests.support.db_connection import clear_data, Session


class TestItem(TestCase):
    @classmethod
    def setUpClass(cls):
        load_dotenv()
    
    def tearDown(self):
        os.remove(os.path.join('bot', 'images', 'profile_items', 'badges', 'wallpaper.png'))
        clear_data(Session())

    def test_save_profile_item(self):
        filename = 'wallpaper.png'
        with open(os.path.join('tests', 'support', filename), 'rb') as f:
            file_contents = f.read()

        profile_item = ProfileItem()
        profile_item.type = 'badge'
        profile_item.name = 'Some item'
        profile_item.price = 100
        
        expected_file_path = os.path.join(
            'bot', 'images', 'profile_items', 'badges', 'wallpaper.png')

        result = asyncio.run(Item().save_profile_item(profile_item, filename, file_contents))

        self.assertIsNotNone(result)
        self.assertEqual(Session().query(ProfileItem).filter_by(id=result).count(), 1)
        self.assertTrue(os.path.exists(expected_file_path))
        with open(expected_file_path, 'rb') as f:
            self.assertEqual(f.read(), file_contents)
