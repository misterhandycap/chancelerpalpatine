import discord
import random
import json
import os
import time
from discord.ext import commands
from bot import client, chess_bot

@client.check
async def globally_block_dms(ctx):
    return ctx.guild is not None

@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.online, activity=discord.Game(f'Planejando uma ordem surpresa'))
    print('Olá, Prime.')

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.BadArgument) and 'User' in str(error) and 'not found' in str(error):
        await ctx.send('Meus scanners não detectaram este usuário.')
    if isinstance(error, commands.CommandNotFound):
        await ctx.send('Comando desconhecido.')
    print(f'{error.__class__}: {error}')

@client.remove_command('help')

@client.command(aliases=['ajuda'])
async def help(ctx, page='1'):
    try:
        page_number = int(page)
    except:
        page_number = 1

    ajuda = discord.Embed(title='Ajuda', description=f'Comandos ({page_number}/2):', colour=discord.Color.blurple(), timestamp=ctx.message.created_at)
    ajuda.set_thumbnail(url='https://cdn.discordapp.com/attachments/676574583083499532/752314249610657932/1280px-Flag_of_the_Galactic_Republic.png')
    if page_number == 1:
        ajuda.add_field(name='tt!ping', value='Confere se o bot está online e sua velocidade de resposta')
        ajuda.add_field(name='tt!clear', value='Limpa o chat, com o padrão sendo 5 mensagens. \n aka:limpar, clean')
        ajuda.add_field(name='tt!vision', value='Faça uma pergunta ao Chanceler e ele irá lhe responder. \n aka:8ball')
        ajuda.add_field(name='tt!sorte', value='Cara ou coroa. \n aka:caracoroa')
        ajuda.add_field(name='tt!level', value='Mostra o nível de usuário ao uúario que pediu \n aka:nivel')
        ajuda.add_field(name='tt!rank', value='Mostra a tabela de niveis de usuários em ordem de maior pra menor \n aka:board')
        ajuda.add_field(name='tt!rps', value='Pedra, papel e tesoura com dinossauros \n aka pedrapapeltesoura, ppt, dino')
    else:
        ajuda.add_field(name='tt!busca', value='Faz uma busca pelo buscador definido (padrão: Google) \n aka google, search, buscar')
        ajuda.add_field(name='tt!xadrez_novo', value='Inicie uma nova partida de xadrez com alguém.\n Passe o ID de usuário para começar uma partida.\n aka:xn')
        ajuda.add_field(name='tt!xadrez_jogar', value='Faça uma jogada em sua partida atual. \n aka:xj')
        ajuda.add_field(name='tt!xadrez_abandonar', value='Abandone a partida atual.\n aka:xa')
        ajuda.add_field(name='tt!xadrez_pgn', value='Gera o PGN da partida atual.\n aka:xpgn')
        ajuda.add_field(name='tt!xadrez_todos', value='Veja todas as partidas que estão sendo jogadas agora.\n aka:xt')
        ajuda.add_field(name='tt!plagueis', value='Conta a tregédia de Darth Plagueis.')
    await ctx.send(embed=ajuda)

@client.command()
async def ping(ctx):
    ping = discord.Embed(title='Pong!', description=f'{round(client.latency * 1000)}ms', colour=discord.Color.blurple(), timestamp=ctx.message.created_at)
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
        await ctx.send('Pergunta não detectada.')

@client.command(aliases=['caracoroa'])
async def sorte(ctx):
    previsao = ['Cara', 'Coroa']
    await ctx.send(f'{random.choice(previsao)}')

@client.command(aliases=['pedrapapeltesoura', 'ppt', 'dino'])
async def rps(ctx, player_choice_str=''):
    player_choice_str = player_choice_str.title()
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

@client.command(aliases=['xn'])
async def xadrez_novo(ctx, user2: discord.User, color_schema=None):
    result = chess_bot.new_game(ctx.author, user2, color_schema=color_schema)
    await ctx.send(result)

@client.command(aliases=['xj'])
async def xadrez_jogar(ctx, move, user2: discord.User=None):
    result, board_png_bytes = chess_bot.make_move(
        ctx.author, move, other_user=user2)
    await ctx.send(result)
    if board_png_bytes:
        await ctx.send(file=discord.File(board_png_bytes, 'board.png'))
        chess_bot.save_games()

        was_last_move_blunder = await chess_bot.is_last_move_blunder(ctx.author, user2)
        if was_last_move_blunder:
            await ctx.send("👀")

@client.command(aliases=['xa'])
async def xadrez_abandonar(ctx, user2: discord.User=None):
    result, board_png_bytes = chess_bot.resign(ctx.author, other_user=user2)
    await ctx.send(result)
    if board_png_bytes:
        await ctx.send(file=discord.File(board_png_bytes, 'board.png'))
        chess_bot.save_games()

@client.command(aliases=['xpgn'])
async def xadrez_pgn(ctx, user2: discord.User=None):
    result = chess_bot.generate_pgn(ctx.author, user2)
    await ctx.send(result)

@client.command(aliases=['xt', 'xadrez_jogos'])
async def xadrez_todos(ctx, page=0):
    png_bytes = chess_bot.get_all_boards_png(page)
    await ctx.send(file=discord.File(png_bytes, 'boards.png'))

@client.command(aliases=['google', 'buscar', 'search'])
async def busca(ctx, *args):
    if not args:
        await ctx.send("O que você quer buscar?")
        return
        
    dicio_serviços = {
        'sww':'https://starwars.fandom.com/pt/wiki/',
        'starwarswiki':'https://starwars.fandom.com/pt/wiki/',
        'wookie':'https://starwars.fandom.com/wiki/',
        'google':'https://www.google.com/search?q=',
        'aw':'https://avatar.fandom.com/pt-br/wiki/',
        'avatar':'https://avatar.fandom.com/pt-br/wiki/',
        'tf':'https://transformers.fandom.com/pt/wiki/',
    }
    
    if args[0].lower() in dicio_serviços:
        buscador = dicio_serviços[args[0].lower()]
        entrada = " ".join(args[1:])
    else:
        buscador = dicio_serviços["google"]
        entrada = " ".join(args)
    await ctx.send(f'{buscador}{entrada.replace(" ", "_")}')
