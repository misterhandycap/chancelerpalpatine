import os
from bot.i18n import _
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont

from bot.astrology.astrology_chart import AstrologyChart
from bot.models.chess_game import ChessGame
from bot.models.profile_item import ProfileItemType
from bot.models.user import User
from bot.models.xp_point import XpPoint


class Profile():

    def __init__(self):
        self.astrology_bot = AstrologyChart()
    
    async def get_user_profile(self, user_id: int, user_avatar: bytes):
        """
        Generates an user profile image banner

        :param user_id: User id
        :type user_id: int
        :param user_avatar: User's avatar
        :type user_avatar: bytes
        :return: User's profile banner
        :rtype: BytesIO
        """
        text_max_width = 10
        
        user = await User.get(user_id, preload_profile_items=True)
        if not user:
            return
        user_profile_badges = [item for item in user.profile_items if item.type == ProfileItemType.badge]
        user_chart = await self.astrology_bot.get_user_chart(user_id)
        user_sign = None
        if user_chart:
            user_sign = self.astrology_bot.get_sun_sign(user_chart)
        user_chess_victories = await ChessGame.get_number_of_victories(user_id)
        user_total_points = await XpPoint.get_user_aggregated_points(user_id)
        if not user_total_points:
            user_total_points = 0

        with open(os.path.join('bot', 'images', 'profile_bg.jpg'), 'rb') as f:
            image_final = Image.open(f)
            image_font_title = ImageFont.truetype(os.environ.get("TRUETYPE_FONT_FOR_PROFILE"), size=48)
            image_font_subtitle = ImageFont.truetype(os.environ.get("TRUETYPE_FONT_FOR_PROFILE"), size=32)
            image_font_description = ImageFont.truetype(os.environ.get("TRUETYPE_FONT_FOR_PROFILE"), size=24)
            image_user_avatar = Image.open(BytesIO(user_avatar))

            image_draw = ImageDraw.Draw(image_final)
            image_draw.text((120, 25), user.name[:15], fill="#FFF", font=image_font_title)
            image_draw.text((30, 635), f'{_("Points")}: {user_total_points}', fill="#FFF", font=image_font_description)
            image_draw.text((400, 620), f'{_("Chess wins")}: {user_chess_victories}', fill="#FFF", font=image_font_subtitle)
            image_draw.text((400, 580), f'{_("Sign")}: {user_sign}', fill="#FFF", font=image_font_subtitle)
            image_final.paste(image_user_avatar.resize((110, 110)), (0, 0))
            image_final = self._draw_user_badges(image_final, user_profile_badges)

        bytesio = BytesIO()
        image_final.save(bytesio, format="png")
        bytesio.seek(0)
        return bytesio

    def _draw_user_badges(self, image, profile_items):
        for index, profile_item in enumerate(profile_items):
            image_bytes_io = profile_item.get_file_contents()
            if not image_bytes_io:
                continue
            image_badge = Image.open(image_bytes_io)
            image_badge_resized = image_badge.resize((60, 60))
            x_position = 450 + index * 70
            if image_badge_resized.mode == 'RGBA':
                image.paste(image_badge_resized, (x_position, 10), mask=image_badge_resized)
            else:
                image.paste(image_badge_resized, (x_position, 10))
        return image
