import requests

def ImportaApendice():
  apendice = "https://starwars.fandom.com/pt/wiki/Predefini%C3%A7%C3%A3o:Tradu%C3%A7%C3%A3oSWW?action=raw"
  r = requests.get(apendice)
  p = r.text.split("{{")
  #Hoje dá para substituir isso por um p[4], mas não sei se isso vai se manter
  #futuro
  p = [item for item in p if item.startswith('{1}}}}')][0]
  p = p.split("\n|")[1:-1]
  #Não vale a pena botar isso em um dicionário, você vai acabar tendo que iterar a lista toda de qualquer maneira.
  return p

def BuscaPalavra(string):
  string = string.lower()+" ="
  apendice = ImportaApendice()
  apendice.append(f"{string} Não encontrado")
  for linha in apendice:
    if linha.startswith(string):
      return linha.split(" = ")[1]
  return linha.split(" = ")[1]
