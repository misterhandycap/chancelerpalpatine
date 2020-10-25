import asyncio
import random
import time
import warnings

from unittest import TestCase
from bot.chess.player import Player
from bot.utils import convert_users_to_players
from tests.support.fake_discord_user import FakeDiscordUser



class TestFight(TestCase):

    def __init__(self):
        self.games = {}

    @classmethod
    def setUpClass(cls):
        warnings.simplefilter('ignore')

    def test_fight(self):
        player1 = FakeDiscordUser(id=1)
        player2 = FakeDiscordUser(id=2)
        move = self.attack, self.defense, self.abandon
        ultima_mesg = 0
        timeout = self.abandon
        if time.time() - ultima_mesg >15:
            return timeout 
        vitoria = self.hp == 0
    
    def test_healthpoints(self):
        self.hp = 100

    def test_defender(self):
        defesa = random.randint(1,10)
        self.defense = self.hp + defesa

    def test_atacar(self):
        self.attack = self.hp - random.randint(1, 15)

    def test_abandonar(self):
        self.abandon = self.hp - 100

    def test_get_user_game(self):
        player: Player = convert_users_to_players(FakeDiscordUser)[0]
        return self.games.get(player.id)
 
