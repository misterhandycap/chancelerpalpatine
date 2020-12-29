import unittest

from bot.traducaosww import BuscaPalavra

class TestTraducao(unittest.TestCase):

    def test_arakein_monks_item_presente(self):
        foo = BuscaPalavra('arakein monks')
        self.assertEqual(foo, "monges Arakein")

    def test_tecnoelfo_item_nao_presente(self):
        foo = BuscaPalavra('tecnoelfo')
        self.assertEqual(foo, 'Não encontrado')
        
if __name__ == '__main__':
    unittest.main()