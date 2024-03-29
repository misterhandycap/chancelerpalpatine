import logging
import os
import warnings

from asyncio import run
from imagehash import average_hash
from PIL import Image
from vcr_unittest import VCRTestCase

from bot.sww.leaderboard import Leaderboard


class TestLeaderboard(VCRTestCase):

    @classmethod
    def setUpClass(cls):
        warnings.simplefilter("ignore")
        logging.disable(logging.WARNING)

    def test_get(self):
        leaderboard_bot = Leaderboard(auto_close_session=True)

        result = run(leaderboard_bot.get())

        self.assertEqual(len(result), 2)
        self.assertIn("dataUser", result[0])
        self.assertGreaterEqual(len(result[1]), 5)

    def test_build_leaderboard_success(self):
        leaderboard_bot = Leaderboard()

        medals = {
            "dataUser": {
                "User1": ["Medal1:1", "Medal2:3"],
                "User2": ["Medal4:1"],
                "User3": ["Medal1:2", "Medal3:4"],
                "User4": ["Medal1:2", "Medal3:1", "Medal2:1"]
            },
            "dataMedal": {
                "Medal1": {
                    "title": "Medal description",
                    "image_url": "some_url"
                },
                "Medal2": {
                    "title": "Medal description",
                    "image_url": "some_url"
                },
                "Medal3": {
                    "title": "Medal description",
                    "image_url": "some_url"
                },
                "Medal4": {
                    "title": "Medal description",
                    "image_url": "some_url"
                },
            }
        }
        medals_points = {
            "Medal1": 50,
            "Medal2": 100,
            "Medal3": 25,
            "Medal4": 500,
            "DescontoInativo": {
                "usuários": ["User3"],
                "desconto": 0.8
            },
            "DescontoAdmin": {
                "usuários": ["User4"],
                "desconto": 0.8
            },
        }
        expected = [
            ('User2', {'points': 500, 'medals': {'Medal4': {'quantity': 1, 'text': 'Medal description', 'image_url': 'some_url'}}}),
            ('User1', {'points': 350, 'medals': {'Medal1': {'quantity': 1, 'text': 'Medal description', 'image_url': 'some_url'}, 'Medal2': {'quantity': 3, 'text': 'Medal description', 'image_url': 'some_url'}}}),
            ('User4', {'points': 180, 'medals': {'Medal1': {'quantity': 2, 'text': 'Medal description', 'image_url': 'some_url'}, 'Medal3': {'quantity': 1, 'text': 'Medal description', 'image_url': 'some_url'}, 'Medal2': {'quantity': 1, 'text': 'Medal description', 'image_url': 'some_url'}}}),
            ('User3', {'points': 160, 'medals': {'Medal1': {'quantity': 2, 'text': 'Medal description', 'image_url': 'some_url'}, 'Medal3': {'quantity': 4, 'text': 'Medal description', 'image_url': 'some_url'}}})
        ]
        
        actual = leaderboard_bot.build_leaderboard(medals, medals_points)

        self.assertEqual(actual, expected)

    def test_build_leaderboard_invalid_parameters(self):
        leaderboard_bot = Leaderboard()

        with self.assertRaises(Exception):
            actual = leaderboard_bot.build_leaderboard("invalid", {})

    def test_build_medals_info(self):
        leaderboard_bot = Leaderboard()
        medals = {
            "dataUser": {
                "User1": ["Medal1:1", "Medal2:3"],
                "User2": ["Medal4:1"],
                "User3": ["Medal1:2", "Medal3:4"],
                "User4": ["Medal1:2", "Medal3:1", "Medal2:1"]
            },
            "dataMedal": {
                "Medal1": {
                    "title": "Medal description",
                    "image_url": "https://vignette.wikia.nocookie.net/pt.starwars/images/2/2e/Medalha_bom.png"
                },
                "Medal2": {
                    "title": "Medal description",
                    "image_url": "https://vignette.wikia.nocookie.net/pt.starwars/images/2/2e/Medalha_bom.png"
                },
                "Medal3": {
                    "title": "Medal description",
                    "image_url": "https://vignette.wikia.nocookie.net/pt.starwars/images/2/2e/Medalha_bom.png"
                },
                "Medal4": {
                    "title": "Medal description",
                    "image_url": "https://vignette.wikia.nocookie.net/pt.starwars/images/2/2e/Medalha_bom.png"
                },
            }
        }
        medals_points = {
            "Medal1": 50,
            "Medal2": 100,
            "Medal3": 25,
            "Medal4": 500,
            "DescontoInativo": {
                "usuários": ["User3"],
                "desconto": 0.8
            },
            "DescontoAdmin": {
                "usuários": ["User4"],
                "desconto": 0.8
            },
        }

        actual = run(leaderboard_bot.build_medals_info(medals, medals_points))
        image_bytes = run(leaderboard_bot._get_image('Medal1', 'https://vignette.wikia.nocookie.net/pt.starwars/images/2/2e/Medalha_bom.png'))

        self.assertEqual(actual, [
            {'name': 'Medal1', 'text': 'Medal description', 'image_url': 'https://vignette.wikia.nocookie.net/pt.starwars/images/2/2e/Medalha_bom.png', 'image': image_bytes, 'points': 50},
            {'name': 'Medal2', 'text': 'Medal description', 'image_url': 'https://vignette.wikia.nocookie.net/pt.starwars/images/2/2e/Medalha_bom.png', 'image': image_bytes, 'points': 100},
            {'name': 'Medal3', 'text': 'Medal description', 'image_url': 'https://vignette.wikia.nocookie.net/pt.starwars/images/2/2e/Medalha_bom.png', 'image': image_bytes, 'points': 25},
            {'name': 'Medal4', 'text': 'Medal description', 'image_url': 'https://vignette.wikia.nocookie.net/pt.starwars/images/2/2e/Medalha_bom.png', 'image': image_bytes, 'points': 500},
        ])
    
    def test_draw_leaderboard_one_page(self):
        leaderboard_bot = Leaderboard(auto_close_session=True)
        leaderboard = [
            ("User2", {'points': 500, 'medals': {'Medal1': {'quantity': 1, 'image_url': 'https://vignette.wikia.nocookie.net/pt.starwars/images/b/b7/Medalha_destaque.png'}}}),
            ("User1LongoNameUser1LongoNameUser1LongoName", {'points': 350, 'medals': {'Medal1': {'quantity': 1, 'image_url': 'https://vignette.wikia.nocookie.net/pt.starwars/images/b/b7/Medalha_destaque.png'},
                'Medal2': {'quantity': 1, 'image_url': 'https://vignette.wikia.nocookie.net/pt.starwars/images/2/2e/Medalha_bom.png'},
                'Medal5': {'quantity': 1, 'image_url': 'https://vignette.wikia.nocookie.net/pt.starwars/images/2/2e/Medalha_bom.png'},
                'Medal3': {'quantity': 1, 'image_url': 'https://vignette.wikia.nocookie.net/pt.starwars/images/2/2e/Medalha_bom.png'}}}),
            ("User3", {'points': 350, 'medals': {'Medal1': {'quantity': 1, 'image_url': 'https://vignette.wikia.nocookie.net/pt.starwars/images/b/b7/Medalha_destaque.png'}, 'Medal2': {'quantity': 1, 'image_url': 'https://vignette.wikia.nocookie.net/pt.starwars/images/2/2e/Medalha_bom.png'}}})
        ]

        actual = run(leaderboard_bot.draw_leaderboard(leaderboard, 1))

        expected_hash = average_hash(Image.open('tests/support/draw_leaderboard.png'))
        actual_hash = average_hash(Image.open(actual))
        self.assertLessEqual(abs(expected_hash - actual_hash), 0)

    def test_draw_leaderboard_second_page(self):
        leaderboard_bot = Leaderboard(auto_close_session=True)
        leaderboard = [
            ("User2", {'points': 500, 'medals': {'Medal1': {'quantity': 1, 'image_url': 'https://vignette.wikia.nocookie.net/pt.starwars/images/b/b7/Medalha_destaque.png'}}}),
            ("User1LongoNameUser1LongoNameUser1LongoName", {'points': 350, 'medals': {'Medal1': {'quantity': 1, 'image_url': 'https://vignette.wikia.nocookie.net/pt.starwars/images/b/b7/Medalha_destaque.png'},
                'Medal2': {'quantity': 1, 'image_url': 'https://vignette.wikia.nocookie.net/pt.starwars/images/2/2e/Medalha_bom.png'},
                'Medal5': {'quantity': 1, 'image_url': 'https://vignette.wikia.nocookie.net/pt.starwars/images/2/2e/Medalha_bom.png'},
                'Medal3': {'quantity': 1, 'image_url': 'https://vignette.wikia.nocookie.net/pt.starwars/images/2/2e/Medalha_bom.png'}}}),
            ("User3", {'points': 350, 'medals': {'Medal1': {'quantity': 1, 'image_url': 'https://vignette.wikia.nocookie.net/pt.starwars/images/b/b7/Medalha_destaque.png'}, 'Medal2': {'quantity': 1, 'image_url': 'https://vignette.wikia.nocookie.net/pt.starwars/images/2/2e/Medalha_bom.png'}}}),
            ("User5", {'points': 350, 'medals': {'Medal1': {'quantity': 1, 'image_url': 'https://vignette.wikia.nocookie.net/pt.starwars/images/b/b7/Medalha_destaque.png'}}}),
            ("User6", {'points': 350, 'medals': {'Medal1': {'quantity': 1, 'image_url': 'https://vignette.wikia.nocookie.net/pt.starwars/images/b/b7/Medalha_destaque.png'}}}),
            ("User7", {'points': 350, 'medals': {'Medal1': {'quantity': 1, 'image_url': 'https://vignette.wikia.nocookie.net/pt.starwars/images/b/b7/Medalha_destaque.png'}}}),
            ("User8", {'points': 350, 'medals': {'Medal1': {'quantity': 1, 'image_url': 'https://vignette.wikia.nocookie.net/pt.starwars/images/b/b7/Medalha_destaque.png'}}}),
            ("User9", {'points': 350, 'medals': {'Medal1': {'quantity': 1, 'image_url': 'https://vignette.wikia.nocookie.net/pt.starwars/images/b/b7/Medalha_destaque.png'}}}),
            ("UserA", {'points': 350, 'medals': {'Medal1': {'quantity': 1, 'image_url': 'https://vignette.wikia.nocookie.net/pt.starwars/images/b/b7/Medalha_destaque.png'}}}),
            ("UserB", {'points': 350, 'medals': {'Medal1': {'quantity': 1, 'image_url': 'https://vignette.wikia.nocookie.net/pt.starwars/images/b/b7/Medalha_destaque.png'}}}),
            ("UserC", {'points': 350, 'medals': {'Medal1': {'quantity': 1, 'image_url': 'https://vignette.wikia.nocookie.net/pt.starwars/images/b/b7/Medalha_destaque.png'}}}),
            ("UserD", {'points': 350, 'medals': {'Medal1': {'quantity': 1, 'image_url': 'https://vignette.wikia.nocookie.net/pt.starwars/images/b/b7/Medalha_destaque.png'}}}),
            ("UserE", {'points': 350, 'medals': {'Medal1': {'quantity': 1, 'image_url': 'https://vignette.wikia.nocookie.net/pt.starwars/images/b/b7/Medalha_destaque.png'}}}),
            ("UserF", {'points': 350, 'medals': {'Medal1': {'quantity': 1, 'image_url': 'https://vignette.wikia.nocookie.net/pt.starwars/images/b/b7/Medalha_destaque.png'}}}),
            ("UserG", {'points': 350, 'medals': {'Medal1': {'quantity': 1, 'image_url': 'https://vignette.wikia.nocookie.net/pt.starwars/images/b/b7/Medalha_destaque.png'}}}),
            ("UserH", {'points': 350, 'medals': {'Medal1': {'quantity': 1, 'image_url': 'https://vignette.wikia.nocookie.net/pt.starwars/images/b/b7/Medalha_destaque.png'}}}),
            ("UserI", {'points': 350, 'medals': {'Medal1': {'quantity': 1, 'image_url': 'https://vignette.wikia.nocookie.net/pt.starwars/images/b/b7/Medalha_destaque.png'}}}),
            ("UserJ", {'points': 350, 'medals': {'Medal1': {'quantity': 1, 'image_url': 'https://vignette.wikia.nocookie.net/pt.starwars/images/b/b7/Medalha_destaque.png'}}}),
            ("UserK", {'points': 350, 'medals': {'Medal1': {'quantity': 1, 'image_url': 'https://vignette.wikia.nocookie.net/pt.starwars/images/b/b7/Medalha_destaque.png'}}}),
            ("UserL", {'points': 350, 'medals': {'Medal1': {'quantity': 1, 'image_url': 'https://vignette.wikia.nocookie.net/pt.starwars/images/b/b7/Medalha_destaque.png'}}}),
        ]

        actual = run(leaderboard_bot.draw_leaderboard(leaderboard, 2))

        expected_hash = average_hash(Image.open(os.path.join('tests', 'support', 'draw_leaderboard_second_page.png')))
        actual_hash = average_hash(Image.open(actual))
        self.assertLessEqual(abs(expected_hash - actual_hash), 0)

    def test_complete_leaderboard_flow(self):
        async def complete_flow(leaderboard_bot):
            try:
                leaderboard_data = await leaderboard_bot.get()
                leaderboard_result = leaderboard_bot.build_leaderboard(*leaderboard_data)
                return await leaderboard_bot.draw_leaderboard(leaderboard_result, 1)
            finally:
                await leaderboard_bot.main_session.close()

        leaderboard_bot = Leaderboard()

        actual = run(complete_flow(leaderboard_bot))

        self.assertIsNotNone(Image.open(actual))
