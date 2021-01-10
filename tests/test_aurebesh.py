from unittest import TestCase

from bot.aurebesh import text_to_aurebesh_img, meme_saimaluco_image


class TestAurebesh(TestCase):

    def test_text_to_aurebesh(self):
        actual = text_to_aurebesh_img('Test 123')

        with open('tests/support/text_to_aurebesh_img.png', 'rb') as f:
            self.assertEqual(actual.getvalue(), f.read())

    def test_meme_saimaluco_image(self):
        actual = meme_saimaluco_image('Test 123 really long text loooongword')

        with open('tests/support/meme_saimaluco_image.png', 'rb') as f:
            self.assertEqual(actual.getvalue(), f.read())
