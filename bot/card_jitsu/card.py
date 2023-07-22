import os
from dataclasses import dataclass

from enum import Enum


class Element(Enum):
    WATER = 1
    SNOW = 2
    FIRE = 3
    
    def __gt__(self, other: 'Element'):
        return self.value == other.value + 1 or self.value - other.value == -2


class Color(Enum):
    RED = 1
    BLUE = 2
    YELLOW = 3
    GREEN = 4
    ORANGE = 5
    PURPLE = 6
    
    def __gt__(self, other: 'Color'):
        return self.value > other.value


@dataclass
class Card():
    id: int
    element: Element
    color: Color
    value: int
    
    @property
    def path(self):
        return os.path.join(os.environ['CARD_JITSU_CARDS_BASE_PATH'], f'{self.id}.png')
    
    def __gt__(self, card: 'Card') -> bool:
        return self.element > card.element or (self.element == card.element and self.value > card.value)
    
    def __eq__(self, card: 'Card') -> bool:
        return self.element == card.element and self.value == card.value
    