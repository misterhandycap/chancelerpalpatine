import asyncio
import warnings

from vcr_unittest import VCRTestCase

from bot.akinator.akinator_game import Akinator, AkinatorGame
from tests.support.fake_discord_user import FakeDiscordUser


class TestAkinatorGame(VCRTestCase):

    @classmethod
    def setUpClass(cls):
        warnings.simplefilter('ignore')

    def _get_vcr(self, **kwargs):
        return super()._get_vcr(match_on=('method', 'scheme', 'host', 'port', 'path'), **kwargs)
    
    def test_new_game(self):
        akinator_bot = AkinatorGame()
        user = FakeDiscordUser(id=14)

        actual = asyncio.run(akinator_bot.new_game(user))

        self.assertEqual(len(actual), 2)
        self.assertIsInstance(actual[0], Akinator)
        self.assertIn('?', actual[1])

    def test_get_user_game_game_exists(self):
        akinator_bot = AkinatorGame()
        user = FakeDiscordUser(id=14)
        akinator_bot.games[user.id] = Akinator()

        actual = akinator_bot.get_user_game(user)

        self.assertIsInstance(actual, Akinator)

    def test_get_user_game_game_does_not_exist(self):
        akinator_bot = AkinatorGame()
        user = FakeDiscordUser(id=14)

        actual = akinator_bot.get_user_game(user)

        self.assertIsNone(actual)

    def test_answer_question_valid_answer(self):
        akinator_bot = AkinatorGame()
        user = FakeDiscordUser(id=14)
        akinator_bot.games[user.id] = Akinator()
        asyncio.run(akinator_bot.games[user.id].start_game())

        actual = asyncio.run(akinator_bot.answer_question(akinator_bot.games[user.id], 'y'))

        self.assertIn('?', actual)

    def test_answer_question_invalid_answer(self):
        akinator_bot = AkinatorGame()
        user = FakeDiscordUser(id=14)
        akinator_bot.games[user.id] = Akinator()
        asyncio.run(akinator_bot.games[user.id].start_game())

        actual = asyncio.run(akinator_bot.answer_question(akinator_bot.games[user.id], 'invalid'))

        self.assertIn('Resposta inválida', actual)

    def test_answer_question_game_over(self):
        akinator_bot = AkinatorGame()
        user = FakeDiscordUser(id=14)
        akinator_bot.games[user.id] = Akinator()
        asyncio.run(akinator_bot.games[user.id].start_game())
        akinator_bot.games[user.id].progression = 85

        actual = asyncio.run(akinator_bot.answer_question(akinator_bot.games[user.id], 'y'))

        self.assertIn('name', actual)
        self.assertIn('description', actual)

