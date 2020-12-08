import json
import requests
import discord
from discord.ext import commands
from bot import client


'''Nós vamos precisar da API de 
1. Medalhas https://starwars.fandom.com/pt/api.php?action=query&format=json&prop=revisions&titles=Star%20Wars%20Wiki%3AMedals%7CStar%20Wars%20Wiki%3AMedals%2FPontos&rvprop=content
2. Usuário
https://services.fandom.com/user-attribute/user/{ID}?format=json
Pegar {ID} na 7ª linha do código fonte e procurar por "ProfileUserId".
IDs conhecidos pela ciência:
Sikon   - 4638
Lele_Mj - 1970153
Thales C- 2112998
JediSam - 3051082
Rapmilo - 24245551
Romerlrl- 25762078


'''
class Wikiano(object):
  def __init__(self, name):
    self.username=name
    m=self.getMedals()
    self.medals=m[1]
    self.points=m[0]
    dicioGetUserData=self.getUserData()
  
  def getMedals(self):
    #Estou usando essa célula
    usuario_a_ser_consultado=self.username
    r = requests.get('https://starwars.fandom.com/pt/api.php?action=query&format=json&prop=revisions&titles=Star%20Wars%20Wiki%3AMedals%7CStar%20Wars%20Wiki%3AMedals%2FPontos&rvprop=content')
    if r.status_code == 200:
        data = json.loads(r.content)
    foo=(data['query']['pages']['28678']['revisions'][0]['*'])
    bar=json.loads(foo)
    dataUser=bar['dataUser']
    #print(dataUser)
    dataMedal=bar['dataMedal']
    foo=(data['query']['pages']['28697']['revisions'][0]['*'])
    dataPontos=json.loads(foo)
    if usuario_a_ser_consultado in dataUser:
      print("...")
      quadro=listaparadicionário(dataUser[usuario_a_ser_consultado])
      total_de_pontos=0
      for k, v in quadro.items():
        total_de_pontos+=(dataPontos[k]*v)
      desconto=[
        usuario_a_ser_consultado in dataPontos['DescontoInativo']['usuários'],
        usuario_a_ser_consultado in dataPontos['DescontoAdmin']['usuários']]
      desconto=0.8 if any(desconto) else 1
      return (total_de_pontos*desconto, quadro)
    else:
      return [0, dict()]

  def getUserData(self):
    #Primeiro descobrir o id do cidadão
    html = requests.get(f"https://starwars.fandom.com/pt/api.php?action=query&list=users&usprop=editcount&ususers={self.username.replace(' ', '_')}&format=json")
    datauser=json.loads(html.content)
    self.id=datauser['query']['users'][0].get('userid')
    if self.id:
      html = requests.get(f"https://starwars.fandom.com/pt/wikia.php?controller=UserProfile&method=getUserData&userId={self.id}&format=json")
      datauser=json.loads(html.content)['userData']
      self.avatar=datauser['avatar']
      self.name=datauser['name']
      self.bio=datauser['bio']
      self.website=datauser['website']
      self.twitter=datauser['twitter']
      self.fbpage=datauser['fbPage']
      self.discordHandle=datauser['discordHandle']
      self.registration=datauser['registration']
      self.posts=datauser['posts']
      self.localEdits=datauser['localEdits']
      self.isBlocked=int(datauser['isBlocked'])
      consulta=f"https://services.fandom.com/user-attribute/user/{str(self.id)}?format=json"
      #print(consulta)
      html = requests.get(consulta)
      datauser=json.loads(html.content)
      #print(datauser)
      datauser=datauser['_embedded']['properties']
      dicio=dict()
      for x in datauser:
        dicio[x['name']]=x['value']
      self.location=dicio.get('location')
      self.name=dicio.get('name')
      self.nickname=dicio.get('nickname')
      self.occupation=dicio.get('ocuppaton')
      self.birthday=dicio.get('UserProfilePagesV3_birthday')
      self.gender=dicio.get('UserProfilePagesV3_gender')
    else:
      print("Essa conta não existe")
      raise ValueError

  def astable(self):
    string=''

    

def listaparadicionário(lista):
  dicio=dict()
  for item in lista:
    key, value = item.split(':')
    if value.isdigit(): 
      value=int(value)
    dicio[key]=value
  return dicio

@client.command(aliases=['w'])
async def wikiuser(ctx, usuario_da_wiki, usuario_do_discord=None):
  if usuario_do_discord is None: usuario_do_discord=ctx.author.name
  try:
    Usuarios[usuario_do_discord]=Wikiano(usuario_da_wiki)
    await ctx.send("Achamos")
  except:
    await ctx.send("Opção inválida")

@client.command(aliases=['bday'])
async def aniversario(ctx, usuario_do_discord=None):
  if usuario_do_discord is not None: usuario_do_discord=ctx.author.name
  bday = Usuarios.get(usuario_do_discord, None)
  if bday is not None and bday.birthday is not None:    
    bday = "/".join(bday.birthday.split("-")[::-1])
    await ctx.send(bday)
  
  
  
    

Usuarios={}
