from unittest import TestCase

from bot.card_jitsu.card import Card, Color, Element
from bot.card_jitsu.deck import Deck
from bot.card_jitsu.player import Player
from tests.support.fake_discord_user import FakeDiscordUser


class TestCardJitsuPlayer(TestCase):
    def setUp(self) -> None:
        self.deck = Deck(cards=[
            Card(id=1, element=Element.SNOW, color=Color.RED, value=2),
            Card(id=2, element=Element.SNOW, color=Color.BLUE, value=2),
            Card(id=3, element=Element.SNOW, color=Color.GREEN, value=2),
            Card(id=4, element=Element.FIRE, color=Color.RED, value=2),
            Card(id=5, element=Element.WATER, color=Color.RED, value=2),
            Card(id=6, element=Element.WATER, color=Color.GREEN, value=2),
            Card(id=7, element=Element.WATER, color=Color.BLUE, value=2),
        ])
        self.player = Player(FakeDiscordUser(id=1), self.deck)
        self.player.hand = self.deck.draw_hand(5)
    
    def test_make_move_legal_move(self):
        self.player.move = None
        
        result = self.player.make_move(3)
        
        self.assertEqual(result, self.player.move)
        self.assertEqual(result, Card(id=4, element=Element.FIRE, color=Color.RED, value=2))
        self.assertEqual(self.player.hand, [
            Card(id=1, element=Element.SNOW, color=Color.RED, value=2),
            Card(id=2, element=Element.SNOW, color=Color.BLUE, value=2),
            Card(id=3, element=Element.SNOW, color=Color.GREEN, value=2),
            Card(id=5, element=Element.WATER, color=Color.RED, value=2),
            Card(id=6, element=Element.WATER, color=Color.GREEN, value=2),
        ])
        self.assertEqual(self.deck.cards, [
            Card(id=7, element=Element.WATER, color=Color.BLUE, value=2),
            Card(id=4, element=Element.FIRE, color=Color.RED, value=2)
        ])
    
    def test_make_move_already_made_move(self):
        self.player.move = Card(id=4, element=Element.FIRE, color=Color.RED, value=2)
        
        with self.assertRaises(Exception) as cm:
            self.player.make_move(3)
            
        self.assertEqual(str(cm.exception), "Player already played their hand this turn")
    
    def test_make_move_ilegal_move(self):
        self.player.move = None
        
        with self.assertRaises(Exception) as cm:
            self.player.make_move(14)
            
        self.assertEqual(str(cm.exception), "Invalid card index")
