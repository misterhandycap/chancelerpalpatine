import os
from unittest import TestCase

from imagehash import average_hash
from PIL import Image

from bot.aurebesh import text_to_aurebesh_img


class TestAurebesh(TestCase):

    def test_text_to_aurebesh(self):
        actual = text_to_aurebesh_img('Test 123')

        expected_hash = average_hash(
            Image.open(os.path.join('tests', 'support', 'text_to_aurebesh_img.png')))
        actual_hash = average_hash(Image.open(actual))
        self.assertLessEqual(abs(expected_hash - actual_hash), 0)
