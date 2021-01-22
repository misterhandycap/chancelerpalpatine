import inspect
import logging

import discord
from discord.ext import commands

from bot.chess.chess import Chess
from bot.chess.puzzle import Puzzle


def get_current_game(func):
    async def function_wrapper(*args, **kwargs):
        this = args[0]
        ctx = args[1]
        user2 = kwargs.get('user2')
        try:
            game = this.chess_bot.find_current_game(ctx.author, user2)
            kwargs['game'] = game
        except Exception as e:
            await ctx.send(str(e))
            return
            
        await func(*args, **kwargs)
    function_wrapper.__name__ = func.__name__
    function_wrapper.__signature__ = inspect.signature(func)
    function_wrapper.__doc__ = func.__doc__
    return function_wrapper


class ChessCog(commands.Cog):
    """
    Comandos para xadrez
    """

    def __init__(self, client):
        self.client = client
        self.chess_bot = Chess()
        self.puzzle_bot = Puzzle()

    @commands.Cog.listener()
    async def on_connect(self):
        await self.chess_bot.load_games()
        logging.info(f'Successfully loaded {len(self.chess_bot.games)} active chess games')
    
    @commands.command(aliases=['xn'])
    async def xadrez_novo(self, ctx, user2: discord.User, color_schema=None):
        """
        Inicie uma nova partida de xadrez com alguém.
        Passe o ID de usuário para começar uma partida
        """
        result = self.chess_bot.new_game(ctx.author, user2, color_schema=color_schema)
        await ctx.send(result)

    @commands.command(aliases=['xpve', 'xcpu', 'xb'])
    async def xadrez_bot(self, ctx, cpu_level: int, color_schema=None):
        """
        Inicie uma nova partida de xadrez contra o bot.
        Passe o nível de dificuldade (de 0 a 20)
        """
        bot_info = await self.client.application_info()
        result = self.chess_bot.new_game(
            ctx.author, bot_info, cpu_level=cpu_level, color_schema=color_schema)
        await ctx.send(result)

    @commands.command(aliases=['xj'])
    @get_current_game
    async def xadrez_jogar(self, ctx, move, *, user2: discord.User=None, **kwargs):
        """
        Faça uma jogada em sua partida atual
        """
        await ctx.trigger_typing()
        game = kwargs['game']
        result, board_png_bytes = await self.chess_bot.make_move(game, move)
        await ctx.send(result)
        if board_png_bytes:
            await ctx.send(file=discord.File(board_png_bytes, 'board.png'))
            await self.chess_bot.save_games()

            evaluation = await self.chess_bot.eval_last_move(game)
            if evaluation["blunder"]:
                await ctx.send("👀")
            elif evaluation["mate_in"] and evaluation["mate_in"] in range(1, 4):
                sheev_msgs = ["DEW IT!", "Mate-o! Mate-o agora!", f"Muito bom, {game.current_player.name}, muito bom!"]
                await ctx.send(sheev_msgs[evaluation["mate_in"] - 1])

    @commands.command(aliases=['xa'])
    @get_current_game
    async def xadrez_abandonar(self, ctx, *, user2: discord.User=None, **kwargs):
        """
        Abandone a partida atual
        """
        await ctx.trigger_typing()
        game = kwargs['game']
        result, board_png_bytes = await self.chess_bot.resign(game)
        await ctx.send(result)
        if board_png_bytes:
            await ctx.send(file=discord.File(board_png_bytes, 'board.png'))
            await self.chess_bot.save_games()

    @commands.command(aliases=['xpgn'])
    @get_current_game
    async def xadrez_pgn(self, ctx, *, user2: discord.User=None, **kwargs):
        """
        Gera o PGN da partida atual
        """
        game = kwargs['game']
        result = self.chess_bot.generate_pgn(game)
        await ctx.send(result)

    @commands.command(aliases=['xt', 'xadrez_jogos'])
    async def xadrez_todos(self, ctx, page=0):
        """
        Veja todas as partidas que estão sendo jogadas agora
        """
        await ctx.trigger_typing()
        png_bytes = await self.chess_bot.get_all_boards_png(page)
        if not png_bytes:
            await ctx.send("Nenhuma partida está sendo jogada... ☹️ Inicie uma com `cp!xadrez_novo`.")
        else:
            await ctx.send(file=discord.File(png_bytes, 'boards.png'))

    @commands.command(aliases=['xgif'])
    async def xadrez_gif(self, ctx, game_id: str, move_number: int, *moves):
        """
        Exibe um GIF animado com uma variante fornecida para o jogo em questão, a partir do lance fornecido

        É necessário passar o jogo em questão, identificado com seu UUID, e o número do lance a partir do qual \
            a sequência fornecida se inicia, que deve ser uma sequência de lances em UCI ou SAN separados por espaço.

        Exemplo de uso: xgif f63e5e4f-dd94-4439-a283-33a1c1a065a0 11 Nxf5 Qxf5 Qxf5 gxf5
        """
        await ctx.trigger_typing()
        chess_game = await self.chess_bot.get_game_by_id(game_id)
        if not chess_game:
            return await ctx.send("Partida não encontrada")
        gif_bytes = await self.chess_bot.build_animated_sequence_gif(chess_game, move_number, moves)
        if not gif_bytes:
            return await ctx.send("Movimento inválido na sequência fornecida")
        return await ctx.send(file=discord.File(gif_bytes, 'variation.gif'))

    @commands.command(aliases=['xp'])
    async def xadrez_puzzle(self, ctx, puzzle_id=None, move=''):
        """
        Pratique um puzzle de xadrez
        """
        await ctx.trigger_typing()
        if not puzzle_id:
            puzzle_dict = await self.puzzle_bot.get_random_puzzle()
            if 'error' in puzzle_dict:
                return await ctx.send(f'Houve um erro ao obter um novo puzzle: {puzzle_dict["error"]}')
            puzzle = self.puzzle_bot.build_puzzle(puzzle_dict)
            if 'error' in puzzle:
                return await ctx.send(f'Houve um erro ao construir um novo puzzle: {puzzle["error"]}')
            return await ctx.send(puzzle["id"], file=discord.File(self.chess_bot.build_png_board(puzzle["game"]), 'puzzle.png'))
        
        puzzle_result = self.puzzle_bot.validate_puzzle_move(puzzle_id, move)
        if isinstance(puzzle_result, str):
            return await ctx.send(puzzle_result)
        
        if puzzle_result:
            if self.puzzle_bot.is_puzzle_over(puzzle_id):
                return await ctx.send("Muito bem, puzzle resolvido 👍")
        if puzzle_result or move == '':
            return await ctx.send(file=discord.File(
                self.chess_bot.build_png_board(self.puzzle_bot.puzzles[puzzle_id]["game"]), 'puzzle.png'))
        
        return await ctx.send("Resposta incorreta")
