from dataclasses import dataclass
from random import shuffle

from bot.card_jitsu.card import Card


@dataclass
class Deck():
    cards: list[Card]
    
    def shuffle(self) -> list[Card]:
        shuffle(self.cards)
        return self.cards
    
    def draw_hand(self, size: int=5) -> list[Card]:
        hand = self.cards[:size]
        self.cards = self.cards[size:]
        return hand
    
    def return_card(self, card: Card) -> list[Card]:
        self.cards.append(card)
        return self.cards
