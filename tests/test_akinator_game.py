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

        actual = asyncio.run(self._new_game(akinator_bot, user))

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

        actual = asyncio.run(self._start_game_and_answer_question(akinator_bot, user.id))

        self.assertIn('?', actual)

    def test_answer_question_invalid_answer(self):
        akinator_bot = AkinatorGame()
        user = FakeDiscordUser(id=14)
        akinator_bot.games[user.id] = Akinator()

        with self.assertRaises(Exception):
            asyncio.run(self._start_game_and_answer_question(
                akinator_bot, user.id, answer='invalid'))

    def test_answer_question_game_over(self):
        akinator_bot = AkinatorGame()
        user = FakeDiscordUser(id=14)
        akinator_bot.games[user.id] = Akinator()

        actual = asyncio.run(self._start_game_and_answer_question(
            akinator_bot, user.id, progression=85))

        self.assertIn('name', actual)
        self.assertIn('description', actual)

    async def _new_game(self, akinator_bot, user):
        try:
            return await akinator_bot.new_game(user, lang='pt')
        finally:
            await akinator_bot.games[user.id].close()
    
    async def _start_game_and_answer_question(self, akinator_bot, user_id, *, progression=None, answer='y'):
        try:
            await akinator_bot.games[user_id].start_game()
            if progression:
                akinator_bot.games[user_id].progression = progression
            
            return await akinator_bot.answer_question(akinator_bot.games[user_id], answer)
        finally:
            await akinator_bot.games[user_id].close()
