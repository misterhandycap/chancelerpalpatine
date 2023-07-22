from unittest import TestCase

from bot.card_jitsu.card import Card, Color, Element
from bot.card_jitsu.deck import Deck
from bot.card_jitsu.game import Game
from bot.card_jitsu.player import Player
from tests.support.fake_discord_user import FakeDiscordUser


class TestCardJitsuGame(TestCase):
    
    def setUp(self) -> None:
        self.deck = Deck(cards=[
            Card(id=1, element=Element.SNOW, color=Color.RED, value=2),
            Card(id=2, element=Element.SNOW, color=Color.BLUE, value=2),
            Card(id=3, element=Element.SNOW, color=Color.GREEN, value=2),
            Card(id=4, element=Element.FIRE, color=Color.RED, value=2),
            Card(id=5, element=Element.WATER, color=Color.RED, value=2),
        ])
        self.player_1 = Player(FakeDiscordUser(id=1), self.deck)
        self.player_2 = Player(FakeDiscordUser(id=2), self.deck)
        
        self.game = Game(self.player_1, self.player_2)
    
    def test_make_player_move(self):
        pass
    
    def test_is_turn_over_no_player_moved(self):
        self.player_1.move = None
        self.player_2.move = None

        self.assertFalse(self.game.is_turn_over())
    
    def test_is_turn_over_only_one_player_moved(self):
        self.player_1.move = Card(id=1, color=Color.RED, element=Element.SNOW, value=3)
        self.player_2.move = None

        self.assertFalse(self.game.is_turn_over())
    
    def test_is_turn_over_both_players_moved(self):
        self.player_1.move = Card(id=1, color=Color.RED, element=Element.SNOW, value=3)
        self.player_2.move = Card(id=1, color=Color.RED, element=Element.WATER, value=2)

        self.assertTrue(self.game.is_turn_over())
    
    def test_score_turn_player_1_wins(self):
        self.player_1.move = Card(id=1, color=Color.RED, element=Element.SNOW, value=3)
        self.player_2.move = Card(id=1, color=Color.RED, element=Element.WATER, value=2)
        
        self.game.score_turn()
        
        self.assertEqual(self.player_1.score, [Card(id=1, color=Color.RED, element=Element.SNOW, value=3)])
        self.assertEqual(self.player_2.score, [])
        self.assertEqual(self.player_1.move, None)
        self.assertEqual(self.player_2.move, None)
    
    def test_score_turn_player_2_wins(self):
        self.player_1.move = Card(id=1, color=Color.RED, element=Element.SNOW, value=2)
        self.player_2.move = Card(id=1, color=Color.RED, element=Element.FIRE, value=3)
        
        self.game.score_turn()
        
        self.assertEqual(self.player_1.score, [])
        self.assertEqual(self.player_2.score, [Card(id=1, color=Color.RED, element=Element.FIRE, value=3)])
        self.assertEqual(self.player_1.move, None)
        self.assertEqual(self.player_2.move, None)
    
    def test_score_turn_draw(self):
        self.player_1.move = Card(id=1, color=Color.RED, element=Element.SNOW, value=2)
        self.player_2.move = Card(id=1, color=Color.RED, element=Element.SNOW, value=2)
        
        self.game.score_turn()
        
        self.assertEqual(self.player_1.score, [])
        self.assertEqual(self.player_2.score, [])
        self.assertEqual(self.player_1.move, None)
        self.assertEqual(self.player_2.move, None)
        
    def test_score_turn_raises_if_any_player_still_needs_to_move(self):
        self.player_1.move = Card(id=1, color=Color.RED, element=Element.SNOW, value=2)
        self.player_2.move = None
        
        with self.assertRaises(Exception) as cm:
            self.game.score_turn()
            
        self.assertEqual(str(cm.exception), 'Both players need to play a card')
    
    def test_winner_by_same_element(self):
        self.player_1.score = [
            Card(id=1, element=Element.SNOW, color=Color.RED, value=2),
            Card(id=2, element=Element.SNOW, color=Color.BLUE, value=2),
            Card(id=3, element=Element.SNOW, color=Color.GREEN, value=2),
        ]
        self.player_2.score = []
        
        self.assertEqual(self.game.winner, self.player_1)
        self.assertTrue(self.game.is_game_over())
    
    def test_winner_by_different_elements(self):
        self.player_1.score = []
        self.player_2.score = [
            Card(id=1, element=Element.SNOW, color=Color.RED, value=2),
            Card(id=2, element=Element.FIRE, color=Color.BLUE, value=2),
            Card(id=3, element=Element.WATER, color=Color.GREEN, value=2),
        ]
        
        self.assertEqual(self.game.winner, self.player_2)
        self.assertTrue(self.game.is_game_over())
    
    def test_winner_none_if_player_has_wrong_color_combination(self):
        self.player_1.score = [
            Card(id=1, element=Element.SNOW, color=Color.RED, value=2),
            Card(id=2, element=Element.FIRE, color=Color.RED, value=2),
            Card(id=3, element=Element.WATER, color=Color.YELLOW, value=2),
            Card(id=4, element=Element.WATER, color=Color.ORANGE, value=2),
        ]
        self.player_2.score = []
        
        self.assertIsNone(self.game.winner)
        self.assertFalse(self.game.is_game_over())
        
    def test_winner_none_if_player_does_not_have_enough_elements(self):
        self.player_1.score = [
            Card(id=1, element=Element.SNOW, color=Color.RED, value=2),
            Card(id=2, element=Element.FIRE, color=Color.RED, value=2),
            Card(id=3, element=Element.SNOW, color=Color.YELLOW, value=2),
            Card(id=4, element=Element.FIRE, color=Color.GREEN, value=2),
            Card(id=5, element=Element.FIRE, color=Color.RED, value=5),
        ]
        self.player_2.score = []
        
        self.assertIsNone(self.game.winner)
        self.assertFalse(self.game.is_game_over())
        
    def test_winner_none_if_player_does_not_have_enough_colors(self):
        self.player_1.score = [
            Card(id=2, element=Element.FIRE, color=Color.RED, value=2),
            Card(id=3, element=Element.WATER, color=Color.RED, value=2),
            Card(id=4, element=Element.SNOW, color=Color.GREEN, value=2),
            Card(id=5, element=Element.FIRE, color=Color.GREEN, value=2),
        ]
        self.player_2.score = []
        
        self.assertIsNone(self.game.winner)
        self.assertFalse(self.game.is_game_over())
