import inspect

import discord

from bot import client, chess_bot

def get_current_game(func):
    async def function_wrapper(*args, **kwargs):
        ctx = args[0]
        user2 = kwargs.get('user2')
        try:
            game = chess_bot.find_current_game(ctx.author, user2)
            kwargs['game'] = game
        except Exception as e:
            await ctx.send(str(e))
            return
            
        await func(*args, **kwargs)
    function_wrapper.__name__ = func.__name__
    function_wrapper.__signature__ = inspect.signature(func)
    return function_wrapper

@client.command(aliases=['xn'])
async def xadrez_novo(ctx, user2: discord.User, color_schema=None):
    result = chess_bot.new_game(ctx.author, user2, color_schema=color_schema)
    await ctx.send(result)

@client.command(aliases=['xj'])
@get_current_game
async def xadrez_jogar(ctx, move, *, user2: discord.User=None, **kwargs):
    game = kwargs['game']
    result, board_png_bytes = chess_bot.make_move(game, move)
    await ctx.send(result)
    if board_png_bytes:
        await ctx.send(file=discord.File(board_png_bytes, 'board.png'))
        chess_bot.save_games()

        was_last_move_blunder = await chess_bot.is_last_move_blunder(game)
        if was_last_move_blunder:
            await ctx.send("👀")

@client.command(aliases=['xa'])
@get_current_game
async def xadrez_abandonar(ctx, *, user2: discord.User=None, **kwargs):
    game = kwargs['game']
    result, board_png_bytes = chess_bot.resign(game)
    await ctx.send(result)
    if board_png_bytes:
        await ctx.send(file=discord.File(board_png_bytes, 'board.png'))
        chess_bot.save_games()

@client.command(aliases=['xpgn'])
@get_current_game
async def xadrez_pgn(ctx, *, user2: discord.User=None, **kwargs):
    game = kwargs['game']
    result = chess_bot.generate_pgn(ctx.author, user2)
    await ctx.send(result)

@client.command(aliases=['xt', 'xadrez_jogos'])
async def xadrez_todos(ctx, page=0):
    png_bytes = chess_bot.get_all_boards_png(page)
    if not png_bytes:
        await ctx.send("Nenhuma partida está sendo jogada... ☹️ Inicie uma com `cp!xadrez_novo`.")
    else:
        await ctx.send(file=discord.File(png_bytes, 'boards.png'))
