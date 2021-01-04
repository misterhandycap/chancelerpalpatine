from vcr_unittest import VCRTestCase

from bot.tradutor import Tradutor

class TestTraducao(VCRTestCase):
    
    def test_arakein_monks_item_presente(self):
        arakein = Tradutor().busca_palavra('arakein monks')
        self.assertEqual(arakein, ('monges Arakein', "''Battlefront: Companhia do Crepúsculo'', traduzido por Leonardo Castilhone"))

    def test_tecnoelfo_item_nao_presente(self):
        tecnoelfo = Tradutor().busca_palavra('tecnoelfo')
        self.assertEqual(tecnoelfo, ('Não encontrada', ''))

    def test_leitura_de_filme(self):
        caretakers = Tradutor().busca_palavra('caretaker')
        self.assertEqual(caretakers, ('Cuidador ', 'Os Últimos Jedi'))

    def test_apos_consulta_objeto_eh_armazenado_no_processed(self):
        obj = Tradutor()
        obj.busca_palavra('force nexus')
        contains = 'force nexus' in obj.processed
        self.assertEqual(contains, True)

    
