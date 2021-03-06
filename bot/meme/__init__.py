import json
import logging
import os
from io import BytesIO
from textwrap import wrap

from aiohttp import ClientSession

from PIL import Image, ImageDraw, ImageFont


def meme_saimaluco_image(text):
    text_max_width = 10
    with open(os.path.join('bot', 'images', 'saimaluco_meme.png'), 'rb') as f:
        image_final = Image.open(f)
        image_font = ImageFont.truetype(os.environ.get("TRUETYPE_FONT_FOR_POINTS_PATH"), size=12)
        image_draw = ImageDraw.Draw(image_final)
        for index, textline in enumerate(wrap(text, text_max_width, break_long_words=False)):
            image_draw.text((30, 30 + 15 * index), textline, fill="#000", font=image_font)

    bytesio = BytesIO()
    image_final.save(bytesio, format="png")
    bytesio.seek(0)
    return bytesio

async def random_cat():
    try:
        async with ClientSession() as session:
            async with session.get("https://aws.random.cat/meow") as response:
                return (await response.json())['file']
    except Exception as e:
        logging.warning(e)
        return None
