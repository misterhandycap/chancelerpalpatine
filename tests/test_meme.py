import os
from asyncio import run
from urllib.parse import urlparse

from imagehash import average_hash
from PIL import Image
from vcr_unittest import VCRTestCase

from bot.meme import meme_saimaluco_image, random_cat


class TestMeme(VCRTestCase):

    def test_meme_saimaluco_image(self):
        actual = meme_saimaluco_image('Test 123 really long text loooongword')

        expected_hash = average_hash(
            Image.open(os.path.join('tests', 'support', 'meme_saimaluco_image.png')))
        actual_hash = average_hash(Image.open(actual))
        self.assertLessEqual(abs(expected_hash - actual_hash), 0)

    def test_random_cat(self):
        image_url = run(random_cat())

        self.assertIsNotNone(urlparse(image_url))
