import os
from copy import deepcopy
from io import BytesIO
from itertools import groupby

from PIL import Image, ImageDraw, ImageFont

from bot.card_jitsu.card import Card, Color, Element
from bot.card_jitsu.deck import Deck
from bot.card_jitsu.game import Game
from bot.card_jitsu.player import Player
from bot.utils import run_cpu_bound_task


class Bot():
    
    def __init__(self) -> None:
        self.games: dict[str, Game] = {}
        self.starter_deck = Deck(cards=[
            Card(id=1, color=Color.BLUE, element=Element.FIRE, value=3),
            Card(id=6, color=Color.PURPLE, element=Element.FIRE, value=6),
            Card(id=9, color=Color.YELLOW, element=Element.FIRE, value=2),
            Card(id=14, color=Color.ORANGE, element=Element.SNOW, value=3),
            Card(id=17, color=Color.RED, element=Element.SNOW, value=2),
            Card(id=20, color=Color.YELLOW, element=Element.SNOW, value=7),
            Card(id=22, color=Color.BLUE, element=Element.WATER, value=5),
            Card(id=23, color=Color.GREEN, element=Element.WATER, value=2),
            Card(id=26, color=Color.PURPLE, element=Element.WATER, value=4),
            Card(id=81, color=Color.GREEN, element=Element.SNOW, value=10),
        ])
        
    def new_game(self, user_1, user_2) -> Game:
        player_1 = Player(user_1, Deck(cards=self.starter_deck.cards.copy()))
        player_2 = Player(user_2, Deck(cards=self.starter_deck.cards.copy()))
        
        if player_1.id in self.games or player_2.id in self.games:
            raise Exception('Player(s) already in a game')
        
        game = Game(player_1, player_2)
        self.games[player_1.id] = game
        self.games[player_2.id] = game
        
        return game
    
    def make_move(self, user, move: int) -> Game:
        player, game = self._find_player_and_game(user)
        player.make_move(move)
        
        return game
    
    @run_cpu_bound_task
    def draw_hand(self, user) -> BytesIO:
        player, _ = self._find_player_and_game(user)
        card_width = 910
        card_height = 1024
        card_padding = 10
        final_image = Image.new('RGB', ((card_width + card_padding) * 5, card_height))
        
        for index, card in enumerate(player.hand):
            card_image = Image.open(card.path)
            card_position = ((card_width + card_padding) * index, 0)
            final_image.paste(card_image.resize((card_width, card_height)), card_position)
            
        bytesio = BytesIO()
        final_image.save(bytesio, format="png")
        bytesio.seek(0)
        return bytesio
    
    @run_cpu_bound_task
    def draw_turn(self, game: Game) -> BytesIO:
        player_1_card = game.player_1.move
        player_2_card = game.player_2.move
        
        game.score_turn()
        
        player_1_score = game.player_1.score
        player_2_score = game.player_2.score
        
        image_width = 2730
        image_height = 2048
        card_width = 910
        card_height = 1024
        final_image = Image.new('RGB', ((image_width, image_height)))
        
        card_vertical_pos = 200
        card_1_image = Image.open(player_1_card.path)
        if player_2_card > player_1_card:
            card_1_image = card_1_image.convert("L")
        card_1_position = (round(card_width * 0.5), card_vertical_pos)
        final_image.paste(card_1_image.resize((card_width, card_height)), card_1_position)
        card_2_image = Image.open(player_2_card.path)
        if player_1_card > player_2_card:
            card_2_image = card_2_image.convert("L")
        card_2_position = (round(card_width * 1.5), card_vertical_pos)
        final_image.paste(card_2_image.resize((card_width, card_height)), card_2_position)
        
        score_vertical_pos = round(card_height * 1.4)
        player_1_score_by_element = {k: list(v) for k, v in groupby(sorted(player_1_score, key=lambda c: c.element), lambda c: c.element)}
        for elem_index, cards in enumerate(player_1_score_by_element.values()):
            for color_index, score in reversed(list(enumerate(cards))):
                score_image = Image.open(score.path)
                score_position = ((elem_index * 300) + round(card_width * .25), score_vertical_pos + color_index * 75)
                score_crop = (15, 15, 235, 235)
                if score.value >= 9:
                    score_crop = (x + 60 for x in score_crop)
                final_image.paste(score_image.resize((card_width, card_height)).crop(score_crop), score_position)
                
        player_2_score_by_element = {k: list(v) for k, v in groupby(sorted(player_2_score, key=lambda c: c.element), lambda c: c.element)}
        for elem_index, cards in enumerate(player_2_score_by_element.values()):
            for color_index, score in reversed(list(enumerate(cards))):
                score_image = Image.open(score.path)
                score_position = ((elem_index * 300) + round(card_width * (3 - .25)) - 900, score_vertical_pos + color_index * 75)
                score_crop = (15, 15, 235, 235)
                if score.value >= 9:
                    score_crop = (x + 60 for x in score_crop)
                final_image.paste(score_image.resize((card_width, card_height)).crop(score_crop), score_position)
                
        image_font_title = ImageFont.truetype(os.environ.get("TRUETYPE_FONT_FOR_PROFILE"), size=72)
        max_user_name_len = 30
        image_draw = ImageDraw.Draw(final_image)
        image_draw.text((120, 25), game.player_1.name[:max_user_name_len], fill="#FFF", font=image_font_title)
        image_draw.text(
            (image_width - 120 - len(game.player_2.name[:max_user_name_len]) * 42, 25),
            game.player_2.name[:max_user_name_len], fill="#FFF", font=image_font_title
        )
        if game.player_1.avatar_bytes:
            image_user_avatar = Image.open(BytesIO(game.player_1.avatar_bytes))
            final_image.paste(image_user_avatar.resize((200, 200)), (120, 125))
        if game.player_2.avatar_bytes:
            image_user_avatar = Image.open(BytesIO(game.player_2.avatar_bytes))
            final_image.paste(image_user_avatar.resize((200, 200)), (120 + round(card_width * 2.5), 125))
        
        bytesio = BytesIO()
        final_image.save(bytesio, format="png")
        bytesio.seek(0)
        return bytesio
        
    def end_game(self, game: Game) -> None:
        del self.games[game.player_1.id]
        del self.games[game.player_2.id]
        
    def _find_player_and_game(self, user) -> tuple[Player, Game]:
        game = self.games.get(user.id, None)
        if game is None:
            raise Exception('User not in a game')
        
        return game.player_1 if game.player_1.id == user.id else game.player_2, game
        
