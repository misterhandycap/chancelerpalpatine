import os
from io import BytesIO
from textwrap import wrap

from PIL import Image, ImageDraw, ImageFont


def text_to_aurebesh_img(text):
    image_font = ImageFont.truetype(os.environ.get("AUREBESH_FONT_PATH"), size=32)
    text_size = image_font.getsize(text)
    image_final = Image.new('RGBA', text_size)
    image_draw = ImageDraw.Draw(image_final)
    image_draw.text((0, 0), text, fill='#52808B', font=image_font)

    bytesio = BytesIO()
    image_final.save(bytesio, format="png")
    bytesio.seek(0)
    return bytesio

def meme_image(text):
    text_max_width = 10
    with open('bot/images/meme.png', 'rb') as f:
        image_final = Image.open(f)
        image_font = ImageFont.truetype(os.environ.get("TRUETYPE_FONT_FOR_POINTS_PATH"), size=12)
        image_draw = ImageDraw.Draw(image_final)
        for index, textline in enumerate(wrap(text, text_max_width, break_long_words=False)):
            image_draw.text((30, 30 + 15 * index), textline, fill="#000", font=image_font)

    bytesio = BytesIO()
    image_final.save(bytesio, format="png")
    bytesio.seek(0)
    return bytesio
