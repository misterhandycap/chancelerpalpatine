import requests

class Tradutor:
  def __init__(self):
    self.importa_apendice()

  def importa_apendice(self):
    apendice = "https://starwars.fandom.com/pt/wiki/Predefini%C3%A7%C3%A3o:Tradu%C3%A7%C3%A3oSWW?action=raw"
    r = requests.get(apendice)
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

  def busca_palavra(self, string):
    string = string.lower()
    return self.dicio.get(string, "Não encontrada")
    
