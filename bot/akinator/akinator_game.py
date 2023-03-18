from typing import Dict, Optional, Tuple, Union
from akinator.async_aki import Akinator

from bot.chess.player import Player
from bot.utils import convert_users_to_players


class AkinatorGame():

    def __init__(self):
        self.games: Dict[int, Akinator] = {}

    async def new_game(self, user, lang: str) -> Tuple[Akinator, str]:
        player: Player = convert_users_to_players(user)[0]
        game = Akinator()
        first_question = await game.start_game(language=lang)
        self.games[player.id] = game
        return game, first_question

    def get_user_game(self, user) -> Optional[Akinator]:
        player: Player = convert_users_to_players(user)[0]
        return self.games.get(player.id)

    async def remove_user_game(self, user):
        player: Player = convert_users_to_players(user)[0]
        await self.games[player.id].close()
        self.games[player.id] = None
    
    async def answer_question(self, game: Akinator, answer: str) -> Union[str, dict]:
        if game.progression > 80:
            return await game.win()
        return await game.answer(answer)
