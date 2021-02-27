import asyncio
from bot.i18n import _

import akinator
from akinator.async_aki import Akinator
from akinator.exceptions import InvalidAnswerError

from bot.chess.player import Player
from bot.utils import convert_users_to_players


class AkinatorGame():

    def __init__(self):
        self.games = {}

    async def new_game(self, user):
        player: Player = convert_users_to_players(user)[0]
        game = Akinator()
        first_question = await game.start_game(language='pt')
        self.games[player.id] = game
        return game, first_question

    def get_user_game(self, user):
        player: Player = convert_users_to_players(user)[0]
        return self.games.get(player.id)
    
    async def answer_question(self, game: Akinator, answer: str):
        if game.progression > 80:
            return await game.win()
        try:
            return await game.answer(answer)
        except InvalidAnswerError:
            return f'{_("Invalid answer. Valid answers are:")} `y`, `n`, `idk`, `p`, `pn`.'
