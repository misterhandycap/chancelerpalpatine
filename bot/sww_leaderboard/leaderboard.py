import json
import os
from io import BytesIO

from aiohttp import ClientSession
from PIL import Image, ImageDraw, ImageFont

from bot.utils import run_cpu_bound_task


class Leaderboard():

    LEADERBOARD_URL = 'https://starwars.fandom.com/pt/api.php?action=query&format=json&prop=revisions&titles=Star%20Wars%20Wiki%3AMedals%7CStar%20Wars%20Wiki%3AMedals%2FPontos&rvprop=content'
    MEDALS_JSON_ID = '28678'
    MEDALS_POINTS_JSON_ID = '28697'
    
    def __init__(self, auto_close_session=False):
        self.auto_close_session = auto_close_session
        self.cache = None
        self.session: ClientSession = None

    async def init_session(self):
        self.session = ClientSession()

    async def get(self):
        if not self.session:
            await self.init_session()
        
        try:
            async with self.session.get(self.LEADERBOARD_URL) as response:
                pages_content = (await response.json())['query']['pages']
                medals = pages_content[self.MEDALS_JSON_ID]['revisions'][0]['*']
                medals_points = pages_content[self.MEDALS_POINTS_JSON_ID]['revisions'][0]['*']
                return json.loads(medals), json.loads(medals_points)
        except (json.JSONDecodeError, KeyError) as e:
            print(e)
            raise Exception("Error parsing content")
        finally:
            if self.auto_close_session:
                await self.close_session()

    def build_leaderboard(self, medals_info, medals_points):
        try:
            users_points = {}
            users = medals_info['dataUser']
            for user_name, user_medals in users.items():
                users_points[user_name] = 0
                for user_medal in user_medals:
                    medal_name, medal_qntity = user_medal.split(":")
                    nerf = medals_points['DescontoInativo']['desconto'] if user_name in medals_points['DescontoInativo']['usuários'] else 1
                    nerf = medals_points['DescontoAdmin']['desconto'] if user_name in medals_points['DescontoAdmin']['usuários'] else nerf
                    users_points[user_name] += int(medals_points[medal_name] * int(medal_qntity) * nerf)
            return sorted(users_points.items(), key=lambda x: x[1], reverse=True)
        except:
            raise Exception('Invalid medals info')

    @run_cpu_bound_task
    def draw_leaderboard(self, leaderboard: list):
        rectangle_height = 50
        image_width = 500
        text_spacing = 10
        font_size = 18
        
        final_image = Image.new('RGB', (image_width, rectangle_height * len(leaderboard)))
        draw_image = ImageDraw.Draw(final_image)
        last_rectangle_pos = 0
        alternate_row_control = True
        for user_name, user_points in leaderboard:
            draw_image.rectangle(
                ((0, last_rectangle_pos), (image_width, last_rectangle_pos + rectangle_height)),
                fill="lightgray" if alternate_row_control else "#CCC"
            )
            draw_image.text(
                (text_spacing, last_rectangle_pos + text_spacing),
                f'{user_name} - {user_points}',
                fill='black',
                font=ImageFont.truetype(os.environ.get("TRUETYPE_FONT_PATH"), size=font_size)
            )
            last_rectangle_pos += rectangle_height
            alternate_row_control = not(alternate_row_control)

        bytesio = BytesIO()
        final_image.save(bytesio, format="png")
        bytesio.seek(0)
        return bytesio

    async def close_session(self):
        await self.session.close()
