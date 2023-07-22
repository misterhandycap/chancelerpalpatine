from bot.card_jitsu.card import Card
from bot.card_jitsu.deck import Deck


class Player():
    def __init__(self, user, deck: Deck):
        self.id: str = user.id
        self.name: str = user.name
        self.avatar_bytes: bytes = None
        self.deck: Deck = deck
        self.score: list[Card] = []
        self.hand: list[Card] = []
        self.move: Card = None
        
    def make_move(self, card_index: int) -> Card:
        if self.move:
            raise Exception("Player already played their hand this turn")
        
        try:
            selected_card = self.hand.pop(card_index)
        except IndexError:
            raise Exception("Invalid card index")
        
        self.move = selected_card
        self.deck.return_card(selected_card)
        self.hand.append(self.deck.draw_hand(1)[0])
        return selected_card

    def __eq__(self, value: 'Player'):
        try:
            return self.id == value.id
        except:
            return False