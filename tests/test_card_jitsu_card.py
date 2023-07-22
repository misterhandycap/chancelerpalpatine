from unittest import TestCase

from bot.card_jitsu.card import Card, Color, Element


class TestCardJitsuCard(TestCase):
    
    def test_gt_by_element(self):
        card_1 = Card(id=1, element=Element.SNOW, color=Color.BLUE, value=3)
        card_2 = Card(id=2, element=Element.WATER, color=Color.BLUE, value=4)
        
        self.assertGreater(card_1, card_2)
        self.assertLess(card_2, card_1)
        self.assertFalse(card_2 > card_1)
        
        card_1 = Card(id=1, element=Element.WATER, color=Color.BLUE, value=3)
        card_2 = Card(id=2, element=Element.FIRE, color=Color.BLUE, value=4)
        
        self.assertGreater(card_1, card_2)
        self.assertLess(card_2, card_1)
        self.assertFalse(card_2 > card_1)
        
        card_1 = Card(id=1, element=Element.SNOW, color=Color.BLUE, value=3)
        card_2 = Card(id=2, element=Element.FIRE, color=Color.BLUE, value=4)
        
        self.assertGreater(card_2, card_1)
        self.assertLess(card_1, card_2)
        self.assertFalse(card_1 > card_2)
    
    def test_gt_by_value(self):
        card_1 = Card(id=1, element=Element.SNOW, color=Color.BLUE, value=6)
        card_2 = Card(id=2, element=Element.SNOW, color=Color.BLUE, value=4)
        
        self.assertGreater(card_1, card_2)
        self.assertLess(card_2, card_1)
        self.assertFalse(card_2 > card_1)
    
    def test_eq(self):
        card_1 = Card(id=1, element=Element.SNOW, color=Color.BLUE, value=6)
        card_2 = Card(id=1, element=Element.SNOW, color=Color.RED, value=6)
        card_3 = Card(id=2, element=Element.SNOW, color=Color.BLUE, value=4)
        card_4 = Card(id=1, element=Element.FIRE, color=Color.BLUE, value=6)
        
        self.assertEqual(card_1, card_2)
        self.assertNotEqual(card_1, card_3)
        self.assertNotEqual(card_1, card_4)
