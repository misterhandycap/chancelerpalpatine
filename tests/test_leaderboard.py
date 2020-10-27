import warnings

from asyncio import run
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
            ("User2", 500),
            ("User1", 350),
            ("User4", 180),
            ("User3", 160)
        ]
        
        actual = leaderboard_bot.build_leaderboard(medals, medals_points)

        self.assertEqual(actual, expected)

    def test_build_leaderboard_invalid_parameters(self):
        leaderboard_bot = Leaderboard()

        with self.assertRaises(Exception):
            actual = leaderboard_bot.build_leaderboard("invalid", {})

    def test_draw_leaderboard(self):
        leaderboard_bot = Leaderboard()
        leaderboard = [
            ("User2", 500),
            ("User1", 350)
        ]

        actual = run(leaderboard_bot.draw_leaderboard(leaderboard))

        with open('tests/support/draw_leaderboard.png', 'rb') as f:
            self.assertEqual(actual.getvalue(), f.read())
