import warnings

from asyncio import run
from PIL import Image
from vcr_unittest import VCRTestCase

from bot.sww_leaderboard.leaderboard import Leaderboard


class TestLeaderboard(VCRTestCase):

    @classmethod
    def setUpClass(cls):
        warnings.simplefilter("ignore")

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

    def test_draw_leaderboard(self):
        leaderboard_bot = Leaderboard(auto_close_session=True)
        leaderboard = [
            ("User2", {'points': 500, 'medals': {'Medal1': {'quantity': 1, 'image_url': 'https://vignette.wikia.nocookie.net/pt.starwars/images/b/b7/Medalha_destaque.png'}}}),
            ("User1LongoNameUser1LongoNameUser1LongoName", {'points': 350, 'medals': {'Medal1': {'quantity': 1, 'image_url': 'https://vignette.wikia.nocookie.net/pt.starwars/images/b/b7/Medalha_destaque.png'},
                'Medal2': {'quantity': 1, 'image_url': 'https://vignette.wikia.nocookie.net/pt.starwars/images/2/2e/Medalha_bom.png'},
                'Medal5': {'quantity': 1, 'image_url': 'https://vignette.wikia.nocookie.net/pt.starwars/images/2/2e/Medalha_bom.png'},
                'Medal3': {'quantity': 1, 'image_url': 'https://vignette.wikia.nocookie.net/pt.starwars/images/2/2e/Medalha_bom.png'}}}),
            ("User3", {'points': 350, 'medals': {'Medal1': {'quantity': 1, 'image_url': 'https://vignette.wikia.nocookie.net/pt.starwars/images/b/b7/Medalha_destaque.png'}, 'Medal2': {'quantity': 1, 'image_url': 'https://vignette.wikia.nocookie.net/pt.starwars/images/2/2e/Medalha_bom.png'}}})
        ]

        actual = run(leaderboard_bot.draw_leaderboard(leaderboard))

        with open('tests/support/draw_leaderboard.png', 'rb') as f:
            self.assertEqual(actual.getvalue(), f.read())

    def test_complete_leaderboard_flow(self):
        async def complete_flow(leaderboard_bot):
            try:
                leaderboard_data = await leaderboard_bot.get()
                leaderboard_result = leaderboard_bot.build_leaderboard(*leaderboard_data)
                return await leaderboard_bot.draw_leaderboard(leaderboard_result)
            finally:
                await leaderboard_bot.main_session.close()

        leaderboard_bot = Leaderboard()

        actual = run(complete_flow(leaderboard_bot))

        self.assertIsNotNone(Image.open(actual))
