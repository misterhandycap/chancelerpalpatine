from vcr_unittest import VCRTestCase

from bot.tradutor import Tradutor

class TestTraducao(VCRTestCase):
    
    def test_arakein_monks_item_presente(self):
        arakein = Tradutor().busca_palavra('arakein monks')
        self.assertEqual(arakein, "monges Arakein")

    def test_tecnoelfo_item_nao_presente(self):
        tecnoelfo = Tradutor().busca_palavra('tecnoelfo')
        self.assertEqual(tecnoelfo, 'Não encontrada')

    
