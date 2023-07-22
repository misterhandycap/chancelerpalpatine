from itertools import groupby

from bot.card_jitsu.card import Element
from bot.card_jitsu.player import Player


class Game():
    player_1: Player
    player_2: Player
    
    def __init__(self, player_1: Player, player_2: Player):
        self.player_1 = player_1
        self.player_2 = player_2
        
        for player in self.players:
            player.deck.shuffle()
            player.hand = player.deck.draw_hand(5)
            player.move = None
            player.score = []
    
    @property
    def players(self) -> list[Player]:
        return [self.player_1, self.player_2]
    
    def is_turn_over(self) -> bool:
        return len([x for x in self.players if x.move is not None]) > 1
    
    def score_turn(self):
        if not self.is_turn_over():
            raise Exception('Both players need to play a card')
        
        winner = max(self.player_1, self.player_2, key=lambda p: p.move)
        score = max(self.player_1.move, self.player_2.move)
        is_draw = self.player_1.move == self.player_2.move
        
        self.player_1.move = None
        self.player_2.move = None
        
        if not is_draw:
            winner.score.append(score)
    
    def is_game_over(self) -> bool:
        return self.winner is not None
    
    @property
    def winner(self) -> Player | None:
        for player in self.players:
            if not player.score:
                continue
            
            score_by_element = {
                k: frozenset([x.color for x in v])
                for k, v in groupby(sorted(player.score, key=lambda c: c.element), lambda c: c.element)
            }
            score_by_color = {
                k: frozenset([x.element for x in v])
                for k, v in groupby(sorted(player.score, key=lambda c: c.color), lambda c: c.color)
            }
            win_by_single_element = len(max(score_by_element.values(), key=len)) >= len(Element)
            win_by_multiple_elements = min(len(set(score_by_color.values())), len(score_by_element)) >= len(Element)
            
            if win_by_single_element or win_by_multiple_elements:
                return player
        return None
