import requests

import re

class Tradutor:
  def __init__(self):
    #self.importa_local()
    #self.importa_template()
    self.raw = dict()
    self.processed = dict()
    self.importa_apendice()
  
  def importa_template(self):
    predef = "https://starwars.fandom.com/pt/wiki/Predefini%C3%A7%C3%A3o:Tradu%C3%A7%C3%A3oSWW?action=raw"
    r = requests.get(predef)
    p = r.text.split("{{")
    #Hoje dá para substituir isso por um p[3], mas não sei se daqui a alguns anos
    #a arquitetura da predefinição seguirá assim.
    p = [item for item in p if item.startswith('{1}}}}')][0]
    p = p.split("\n|")[1:-1]
    #Não vale a pena botar isso em um dicionário, você vai acabar tendo que iterar a lista toda de qualquer maneira.
    self.dicio = dict()
    for item in p:
      k, v = item.split(" = ")
      self.dicio[k] = v

  def importa_apendice(self):
    apendice = "https://starwars.fandom.com/pt/wiki/Star_Wars_Wiki:Ap%C3%AAndice_de_Tradu%C3%A7%C3%A3o?action=raw"
    r = requests.get(apendice)
    EhEntrada = lambda n: n.startswith("*")
    self.dicio = dict()
    for linha in r.text.split('\n'):
      if linha.startswith("*"):
        self.raw[linha.split("=")[0][1:-1].lower()] = linha

  def importa_local(self):
    self.dicio = dict()
    self.L=[]
    with open('apendiceLocal.txt', 'r', encoding='utf-8') as e:
      for linha in e:
        if linha.startswith("*"):
          self.formata(linha)
            
  def busca_palavra(self, string):
    #verifica se já foi tratado
    chave = self.processed.get(string, None)
    string = string.lower()
    if chave:
      return chave
    chave = self.raw.get(string, None)
    string = '*'+string.lower()

    if chave:
      nova_chave = self.formata(chave)
      return nova_chave
    return ("Não encontrada", "")
      

  def formata(self, entrada):
    #removendo quebras de linhas
    entrada = entrada.replace("\n", "")
    #dividindo chave e valor
    chave, padrao = entrada.split(' = ', 1)
    chave = chave.lower()[1:]
    #tirando as <ref>
    refs=r'<[^>]*.'          #<...>
    padrao = re.sub(refs, "::", padrao)
    #tirando o [[link|
    link = r'\[\[[^\|]*\|'  #[[...|
    padrao = re.sub(link, "", padrao)
    #tirando o [[]]
    colchetes = r'[\[\]]'
    padrao = re.sub(colchetes, "", padrao)
    tupla = padrao.split("::", 1)+['']
    tupla[1] = tupla[1].replace("::", ": ").replace(": :", ": ")
    self.processed[chave]=tuple(tupla[:2])
    return tuple(tupla[:2])

