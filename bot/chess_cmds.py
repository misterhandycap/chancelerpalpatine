import inspect

import discord

from bot import client, chess_bot, puzzle_bot

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
    function_wrapper.__doc__ = func.__doc__
    return function_wrapper

@client.command(aliases=['xn'])
async def xadrez_novo(ctx, user2: discord.User, color_schema=None):
    """
    Inicie uma nova partida de xadrez com alguém.
    Passe o ID de usuário para começar uma partida
    """
    result = chess_bot.new_game(ctx.author, user2, color_schema=color_schema)
    await ctx.send(result)

@client.command(aliases=['xpve', 'xcpu', 'xb'])
async def xadrez_bot(ctx, cpu_level: int, color_schema=None):
    """
    Inicie uma nova partida de xadrez contra o bot.
    Passe o nível de dificuldade (de 0 a 20)
    """
    bot_info = await client.application_info()
    result = chess_bot.new_game(
        ctx.author, bot_info, cpu_level=cpu_level, color_schema=color_schema)
    await ctx.send(result)

@client.command(aliases=['xj'])
@get_current_game
async def xadrez_jogar(ctx, move, *, user2: discord.User=None, **kwargs):
    """
    Faça uma jogada em sua partida atual
    """
    await ctx.trigger_typing()
    game = kwargs['game']
    result, board_png_bytes = await chess_bot.make_move(game, move)
    await ctx.send(result)
    if board_png_bytes:
        await ctx.send(file=discord.File(board_png_bytes, 'board.png'))
        chess_bot.save_games()

        evaluation = await chess_bot.eval_last_move(game)
        if evaluation["blunder"]:
            await ctx.send("👀")
        elif evaluation["mate_in"] and evaluation["mate_in"] in range(1, 4):
            sheev_msgs = ["DEW IT!", "Mate-o! Mate-o agora!", f"Muito bom, {game.current_player.name}, muito bom!"]
            await ctx.send(sheev_msgs[evaluation["mate_in"] - 1])

@client.command(aliases=['xa'])
@get_current_game
async def xadrez_abandonar(ctx, *, user2: discord.User=None, **kwargs):
    """
    Abandone a partida atual
    """
    await ctx.trigger_typing()
    game = kwargs['game']
    result, board_png_bytes = chess_bot.resign(game)
    await ctx.send(result)
    if board_png_bytes:
        await ctx.send(file=discord.File(board_png_bytes, 'board.png'))
        chess_bot.save_games()

@client.command(aliases=['xpgn'])
@get_current_game
async def xadrez_pgn(ctx, *, user2: discord.User=None, **kwargs):
    """
    Gera o PGN da partida atual
    """
    game = kwargs['game']
    result = chess_bot.generate_pgn(game)
    await ctx.send(result)

@client.command(aliases=['xt', 'xadrez_jogos'])
async def xadrez_todos(ctx, page=0):
    """
    Veja todas as partidas que estão sendo jogadas agora
    """
    await ctx.trigger_typing()
    png_bytes = await chess_bot.get_all_boards_png(page)
    if not png_bytes:
        await ctx.send("Nenhuma partida está sendo jogada... ☹️ Inicie uma com `cp!xadrez_novo`.")
    else:
        await ctx.send(file=discord.File(png_bytes, 'boards.png'))

@client.command(aliases=['xp'])
async def xadrez_puzzle(ctx, puzzle_id=None, move=''):
    """
    Pratique um puzzle de xadrez
    """
    await ctx.trigger_typing()
    if not puzzle_id:
        puzzle_dict = await puzzle_bot.get_random_puzzle()
        if 'error' in puzzle_dict:
            return await ctx.send(f'Houve um erro ao obter um novo puzzle: {puzzle_dict["error"]}')
        puzzle = puzzle_bot.build_puzzle(puzzle_dict)
        if 'error' in puzzle:
            return await ctx.send(f'Houve um erro ao construir um novo puzzle: {puzzle["error"]}')
        return await ctx.send(puzzle["id"], file=discord.File(chess_bot.build_png_board(puzzle["game"]), 'puzzle.png'))
    
    puzzle_result = puzzle_bot.validate_puzzle_move(puzzle_id, move)
    if isinstance(puzzle_result, str):
        return await ctx.send(puzzle_result)
    
    if puzzle_result:
        if puzzle_bot.is_puzzle_over(puzzle_id):
            return await ctx.send("Muito bem, puzzle resolvido 👍")
    if puzzle_result or move == '':
        return await ctx.send(file=discord.File(
            chess_bot.build_png_board(puzzle_bot.puzzles[puzzle_id]["game"]), 'puzzle.png'))
    
    return await ctx.send("Resposta incorreta")
