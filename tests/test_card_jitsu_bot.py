import asyncio
import os
from io import BytesIO
from unittest import TestCase

from dotenv import load_dotenv

from bot.card_jitsu.bot import Bot
from bot.card_jitsu.card import Card
from bot.card_jitsu.deck import Deck
from bot.card_jitsu.game import Game
from bot.card_jitsu.player import Player
from tests.support.fake_discord_user import FakeDiscordUser


class TestCardJitsuBot(TestCase):
    
    @classmethod
    def setUpClass(cls) -> None:
        load_dotenv()
    
    def test_new_game_success(self):
        bot = Bot()
        user_1 = FakeDiscordUser(id=1)
        user_2 = FakeDiscordUser(id=2)
        
        result = bot.new_game(user_1, user_2)
        
        self.assertIsInstance(result, Game)
        self.assertEqual(result.player_1.id, user_1.id)
        self.assertEqual(result.player_2.id, user_2.id)
        self.assertNotEqual(result.player_1.deck, result.player_2.deck)
        self.assertNotEqual(result.player_1.hand, result.player_2.hand)
        self.assertEqual(len(result.player_1.hand), 5)
        self.assertEqual(len(result.player_2.hand), 5)
        self.assertEqual(len(result.player_1.deck.cards), 5)
        self.assertEqual(len(result.player_2.deck.cards), 5)
        
    def test_new_game_raises_if_any_user_is_already_playing(self):
        bot = Bot()
        user_1 = FakeDiscordUser(id=1)
        user_2 = FakeDiscordUser(id=2)
        bot.games[user_1.id] = "some game"
        
        with self.assertRaises(Exception) as cm:
            bot.new_game(user_1, user_2)
        
        self.assertEqual(str(cm.exception), "Player(s) already in a game")
    
    def test_make_move_valid_move(self):
        bot = Bot()
        user_1 = FakeDiscordUser(id=1)
        player_1 = Player(user_1, bot.starter_deck)
        player_2 = Player(FakeDiscordUser(id=2), bot.starter_deck)
        game = Game(player_1, player_2)
        bot.games[player_1.id] = game
        
        result = bot.make_move(user_1, 4)
        
        self.assertEqual(result, game)
        self.assertIsInstance(player_1.move, Card)
    
    def test_make_move_raises_if_user_is_not_playing(self):
        bot = Bot()
        user_1 = FakeDiscordUser(id=1)
        
        with self.assertRaises(Exception) as cm:
            bot.make_move(user_1, 4)
        
        self.assertEqual(str(cm.exception), "User not in a game")
    
    def test_draw_hand(self):
        bot = Bot()
        player_1 = Player(FakeDiscordUser(id=1), Deck(cards=bot.starter_deck.cards.copy()))
        player_2 = Player(FakeDiscordUser(id=2), Deck(cards=bot.starter_deck.cards.copy()))
        game = Game(player_1, player_2)
        bot.games[player_1.id] = game
        player_1.hand = bot.starter_deck.cards[:5]
        
        image_bytesio = asyncio.run(bot.draw_hand(player_1))

        with open(os.path.join('tests', 'support', 'draw_hand.png'), 'rb') as f:
            self.assertEqual(image_bytesio.read(), f.read())
            # f.write(image_bytesio.getbuffer())
    
    def test_draw_turn(self):
        bot = Bot()
        player_1 = Player(FakeDiscordUser(id=1, name='User 1'), Deck(cards=bot.starter_deck.cards.copy()))
        player_2 = Player(FakeDiscordUser(id=2, name='User 2 very long name'), Deck(cards=bot.starter_deck.cards.copy()))
        with open(os.path.join('tests', 'support', 'user_avatar.png'), 'rb') as f:
            user_avatar_bytes = f.read()
        player_1.avatar_bytes = user_avatar_bytes
        player_2.avatar_bytes = user_avatar_bytes
        game = Game(player_1, player_2)
        player_1.move = bot.starter_deck.cards[0]
        player_2.move = bot.starter_deck.cards[5]
        player_1.score = bot.starter_deck.cards
        player_2.score = list(reversed(bot.starter_deck.cards))
        
        image_bytesio = asyncio.run(bot.draw_turn(game))

        with open(os.path.join('tests', 'support', 'draw_turn.png'), 'rb') as f:
            self.assertEqual(image_bytesio.read(), f.read())
