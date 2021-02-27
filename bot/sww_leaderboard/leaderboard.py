import json
import logging
import os
from asyncio import as_completed
from bot.i18n import _
from io import BytesIO

from aiohttp import ClientSession
from PIL import Image, ImageDraw, ImageFont

from bot.utils import paginate, run_cpu_bound_task, run_cpu_bound_task_with_event_loop


class Leaderboard():

    LEADERBOARD_URL = 'https://starwars.fandom.com/pt/api.php?action=query&format=json&prop=revisions&titles=Star%20Wars%20Wiki%3AMedals%7CStar%20Wars%20Wiki%3AMedals%2FPontos&rvprop=content'
    MEDALS_JSON_ID = '28678'
    MEDALS_POINTS_JSON_ID = '28697'
    
    def __init__(self, auto_close_session=False):
        self.auto_close_session = auto_close_session
        self.medals_image_cache = {}
        self.main_session: ClientSession = None
        self.threaded_session: ClientSession = None

    async def get(self):
        if not self.main_session:
            self.main_session = ClientSession()
        
        try:
            async with self.main_session.get(self.LEADERBOARD_URL) as response:
                pages_content = (await response.json())['query']['pages']
                medals = pages_content[self.MEDALS_JSON_ID]['revisions'][0]['*']
                medals_points = pages_content[self.MEDALS_POINTS_JSON_ID]['revisions'][0]['*']
                return json.loads(medals), json.loads(medals_points)
        except (json.JSONDecodeError, KeyError) as e:
            logging.warning(e, exc_info=True)
            raise Exception(_("Error parsing content"))
        finally:
            if self.auto_close_session:
                await self.main_session.close()

    def build_leaderboard(self, medals_info, medals_points):
        try:
            leaderboard_users = {}
            users = medals_info['dataUser']
            for user_name, user_medals in users.items():
                leaderboard_users[user_name] = {'points': 0, 'medals': {}}
                for user_medal in user_medals:
                    medal_name, medal_qntity = user_medal.split(":")
                    medal_info = medals_info['dataMedal'][medal_name]
                    nerf = medals_points['DescontoInativo']['desconto'] if user_name in medals_points['DescontoInativo']['usuários'] else 1
                    nerf = medals_points['DescontoAdmin']['desconto'] if user_name in medals_points['DescontoAdmin']['usuários'] else nerf
                    leaderboard_users[user_name]['points'] += int(medals_points[medal_name] * int(medal_qntity) * nerf)
                    leaderboard_users[user_name]['medals'][medal_name] = {
                        'quantity': int(medal_qntity),
                        'text': medal_info['title'],
                        'image_url': medal_info['image_url']
                    }
            return sorted(leaderboard_users.items(), key=lambda x: x[1]['points'], reverse=True)
        except Exception as e:
            logging.warning(e, exc_info=True)
            raise Exception(_('Invalid medals info'))

    async def build_medals_info(self, medals_info, medals_points):
        medals = []
        unique_medals = [(medal_name, medal_info['image_url']) for medal_name, medal_info in medals_info['dataMedal'].items()]
        await self._prepare_medals_images(unique_medals)
        for medal_name, medal_info in medals_info['dataMedal'].items():
            medals.append({
                'name': medal_name,
                'text': medal_info['title'],
                'image_url': medal_info['image_url'],
                'image': await self._get_image(medal_name, medal_info['image_url']),
                'points': int(medals_points[medal_name])
            })
        return medals

    @run_cpu_bound_task
    @run_cpu_bound_task_with_event_loop
    async def draw_leaderboard(self, leaderboard: list, page: int):
        rectangle_height = 50
        image_width = 500
        text_spacing = 10
        font_size = 18
        medal_size = 30
        max_users_per_page = 10
        paginated_leaderboard, _ = paginate(leaderboard, page, max_users_per_page)
        medal_positions = [5, int(medal_size * 0.5), int(medal_size * 0.833)]

        unique_medals = set([(medal, user_info[1]['medals'][medal]['image_url']) for user_info in leaderboard for medal in user_info[1]['medals']])
        await self._prepare_medals_images(unique_medals)
        
        final_image = Image.new('RGB', (image_width, rectangle_height * min(len(leaderboard), max_users_per_page)))
        draw_image = ImageDraw.Draw(final_image)
        last_rectangle_pos = 0
        alternate_row_control = True
        for user_name, user_info in paginated_leaderboard:
            draw_image.rectangle(
                ((0, last_rectangle_pos), (image_width, last_rectangle_pos + rectangle_height)),
                fill="#D3D3D3" if alternate_row_control else "#CCC"
            )
            if last_rectangle_pos:
                draw_image.line(
                    ((0, last_rectangle_pos), (image_width, last_rectangle_pos)),
                    fill='#A9A9A9'
                )
            draw_image.text(
                (medal_size * 2 + text_spacing, last_rectangle_pos + text_spacing),
                '{:.20}'.format(user_name),
                fill='#2E2E2E',
                font=ImageFont.truetype(os.environ.get("TRUETYPE_FONT_FOR_USERS_PATH"), size=font_size)
            )
            draw_image.text(
                (image_width - int(5 * font_size * 0.7), last_rectangle_pos + text_spacing),
                '{:5}'.format(user_info["points"]),
                fill='#2E2E2E',
                font=ImageFont.truetype(os.environ.get("TRUETYPE_FONT_FOR_POINTS_PATH"), size=font_size + 2)
            )
            last_medal_pos = medal_positions[min(max(len(user_info['medals']) - 1, 0), 2)]
            for medal_name, medal_info in user_info['medals'].items():
                medal_image = Image.open(
                    BytesIO(await self._get_image(medal_name, medal_info['image_url']))
                ).convert('RGBA').resize((medal_size, medal_size))
                final_image.paste(
                    medal_image,
                    (last_medal_pos, last_rectangle_pos + text_spacing),
                    mask=medal_image
                )
                if not medal_positions.index(last_medal_pos):
                    break
                last_medal_pos = medal_positions[medal_positions.index(last_medal_pos) - 1]
            last_rectangle_pos += rectangle_height
            alternate_row_control = not(alternate_row_control)

        bytesio = BytesIO()
        final_image.save(bytesio, format="png")
        bytesio.seek(0)
        return bytesio

    async def _prepare_medals_images(self, unique_medals):
        self.threaded_session = ClientSession()
        
        for r in as_completed([self._get_image(name, url) for name, url in unique_medals]):
            await r
        await self.threaded_session.close()
    
    async def _get_image(self, medal_name, image_url):
        if medal_name in self.medals_image_cache:
            return self.medals_image_cache[medal_name]
        
        async with self.threaded_session.get(image_url) as response:
            response_bytes = await response.read()
            self.medals_image_cache[medal_name] = response_bytes
            return response_bytes
