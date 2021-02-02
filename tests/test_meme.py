from asyncio import run
from urllib.parse import urlparse

from vcr_unittest import VCRTestCase

from bot.meme import meme_saimaluco_image, random_cat


class TestMeme(VCRTestCase):

    def test_meme_saimaluco_image(self):
        actual = meme_saimaluco_image('Test 123 really long text loooongword')

        with open('tests/support/meme_saimaluco_image.png', 'rb') as f:
            self.assertEqual(actual.getvalue(), f.read())

    def test_random_cat(self):
        image_url = run(random_cat())

        self.assertIsNotNone(urlparse(image_url))
