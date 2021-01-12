import os
from io import BytesIO

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
