from unittest import TestCase

from bot.meme import meme_saimaluco_image


class TestMeme(TestCase):

    def test_meme_saimaluco_image(self):
        actual = meme_saimaluco_image('Test 123 really long text loooongword')

        with open('tests/support/meme_saimaluco_image.png', 'rb') as f:
            self.assertEqual(actual.getvalue(), f.read())
