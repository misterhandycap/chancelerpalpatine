from unittest import TestCase

from bot.utils import paginate


class TestUtils(TestCase):
    
    def test_paginate_first_page(self):
        elems = [1, 2, 3, 4, 5, 6]
        max_itens = 5
        page = 1

        result = paginate(elems, page, max_itens)

        self.assertEqual(result[0], elems[:5])
        self.assertEqual(result[1], 2)

    def test_paginate_last_page(self):
        elems = [1, 2, 3, 4, 5, 6]
        max_itens = 5
        page = 2

        result = paginate(elems, page, max_itens)

        self.assertEqual(result[0], elems[5:])
        self.assertEqual(result[1], 2)

    def test_paginate_invalid_page_low(self):
        elems = [1, 2, 3, 4, 5, 6]
        max_itens = 5
        page = 0

        result = paginate(elems, page, max_itens)

        self.assertEqual(result[0], elems[:5])
        self.assertEqual(result[1], 2)

    def test_paginate_invalid_page_high(self):
        elems = [1, 2, 3, 4, 5, 6]
        max_itens = 5
        page = 10

        result = paginate(elems, page, max_itens)

        self.assertEqual(result[0], elems[:5])
        self.assertEqual(result[1], 2)
