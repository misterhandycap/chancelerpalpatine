import asyncio
import random
import time

from bot.chess.player import Player
from bot.utils import convert_users_to_players



class Fight():

    def __init__(self):
        self.games = {}

    def fight(self, user1, user2):
        player1, player2 = convert_users_to_players(user1, user2)
        move = self.attack, self.defense, self.abandon
        ultima_mesg = 0
        timeout = self.abandon
        if time.time() - ultima_mesg >15:
            return timeout 
        vitoria = self.hp == 0
    
    def healthpoints(self, hp):
        self.hp = 100

    def defender(self, defesa, defense):
        defesa = random.randint(1,10)
        self.defense = self.hp + defesa

    def atacar(self, attack):
        self.attack = self.hp - random.randint(1, 15)

    def abandonar(self, abandon):
        self.abandon = self.hp - 100

    def get_user_game(self, user):
        player: Player = convert_users_to_players(user)[0]
        return self.games.get(player.id)
 
