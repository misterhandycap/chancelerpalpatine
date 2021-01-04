from unittest import TestCase

from bot.utils import paginate, find_best_url


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

        self.assertEqual(result[0], elems[5:])
        self.assertEqual(result[1], 2)

    def test_return_canon_at_find_best_url(self):
        grogu = find_best_url('Grogu')
        self.assertEqual(grogu, 'https://starwars.fandom.com/pt/wiki/Grogu')

    def test_return_legends_at_find_best_url(self):
        jaina = find_best_url('Rei')
        self.assertEqual(jaina, 'https://starwars.fandom.com/pt/wiki/Legends:Rei')
        
    def test_return_wookie_at_find_best_url(self):
        ligalac = find_best_url('Library Galactica', 1)
        self.assertEqual(ligalac, 'https://starwars.fandom.com/wiki/Library_Galactica')

    def test_invalid_input_at_find_best_url(self):
        sequels = find_best_url('sequels kkkk')
        self.assertEqual(sequels, None)
