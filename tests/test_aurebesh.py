import os
from unittest import TestCase

from bot.aurebesh import text_to_aurebesh_img


class TestAurebesh(TestCase):

    def test_text_to_aurebesh(self):
        actual = text_to_aurebesh_img('Test 123')

        with open(os.path.join('tests', 'support', 'text_to_aurebesh_img.png'), 'rb') as f:
            self.assertEqual(actual.getvalue(), f.read())
