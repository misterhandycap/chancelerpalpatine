import discord
import random
import json
import os
import time
from discord.ext import commands
from bot import client

@client.check
async def globally_block_dms(ctx):
    return ctx.guild is not None

@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.online, activity=discord.Game(f'Planejando uma ordem surpresa'))
    print('É bom te ver, mestre Jedi.')

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredPermissions):
        await ('Parece que você não tem poder aqui, Jedi, cheque com os mestres do Conselho e volte mais tarde.')

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send('Esta ordem não existe, agora se me der licença...')

@client.remove_command('help')

@client.command(aliases=['ajuda'])
async def help(ctx):
    ajuda = discord.Embed(title='Ajuda', description='Comandos:', colour=discord.Color.blurple(), timestamp=ctx.message.created_at)
    ajuda.set_thumbnail(url='https://cdn.discordapp.com/attachments/676574583083499532/752314249610657932/1280px-Flag_of_the_Galactic_Republic.png')
    ajuda.add_field(name='cp!ping', value='Confere se o bot está online e sua velocidade de resposta')
    ajuda.add_field(name='cp!clear', value='Limpa o chat, com o padrão sendo 5 mensagens. \n aka:limpar, clean')
    ajuda.add_field(name='cp!vision', value='Faça uma pergunta ao Chanceler e ele irá lhe responder. \n aka:8ball')
    ajuda.add_field(name='cp!sorte', value='Cara ou coroa. \n aka:caracoroa')
    ajuda.add_field(name='cp!level', value='Mostra o nível de usuário ao uúario que pediu \n aka:nivel')
    ajuda.add_field(name='cp!rank', value='Mostra a tabela de niveis de usuários em ordem de maior pra menor \n aka:board')
    ajuda.add_field(name='cp!rps', value='Pedra, papel e tesoura com dinossauros \n aka pedrapapeltesoura, ppt, dino')
    await ctx.send(embed=ajuda)

@client.command()
async def ping(ctx):
    ping = discord.Embed(title='Pong...', description=f'{round(client.latency * 1000)}ms', colour=discord.Color.blurple(), timestamp=ctx.message.created_at)
    await ctx.send(embed=ping)

@client.command(aliases=['limpar', 'clean'])
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount=5+1):
    await ctx.channel.purge(limit=amount)

@client.command(aliases=['8ball'])
async def vision(ctx, *, question):
    responses = ['Assim é.', 'Está me ameaçando?', 'É certo.', 'Acho que devemos buscar mais informações.', 'Isso não está correto.', 'Você está errado(a).', 'Não, não, NÃO!!', 'Acredito que esteja errado(a), Mestre', 'Isso necessita de mais análises']
    await ctx.send(f'{random.choice(responses)}')

@vision.error
async def clear_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Queria me perguntar algo, Jedi?')

@client.command(aliases=['caracoroa'])
async def sorte(ctx):
    previsao = ['Cara', 'Coroa']
    await ctx.send(f'{random.choice(previsao)}')

@client.command(aliases=['pedrapapeltesoura', 'ppt', 'dino'])
async def rps(ctx):
    player_choice_str = ctx.message.content.lower().replace('cp!rps', '').strip().title()
    available_options = ['Deus', 'Homem', 'Dinossauro']
    if player_choice_str not in available_options:
        await ctx.send("Opção inválida")
        return

    player_choice = available_options.index(player_choice_str)
    bot_choice = random.randint(0,2)
    bot_choice_str = available_options[bot_choice]

    if bot_choice == player_choice:
        #empate
        result = "Mulher herda a Terra"
    else:
        winner_choice = max(bot_choice, player_choice) if abs(bot_choice - player_choice) == 1 else min(bot_choice, player_choice)
        action_txt = ' destrói '
        if winner_choice == player_choice:
            who = 'Você ganhou o jogo'
            winner, loser = player_choice_str, bot_choice_str
        else:
            who = 'Você perdeu o jogo'
            winner, loser = bot_choice_str, player_choice_str
        if winner == 'dinossauro':
            action_txt = ' come o '
        result = f'{winner}{action_txt}{loser}\n{who}'

    resp_message = f"O bot escolheu: {bot_choice_str}\n{result}"
    #result+='\n\nTodo sábado sessão de Jurassic Park na SWW'
    await ctx.send(resp_message)




#os.system('python level.py')
