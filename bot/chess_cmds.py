import inspect
import logging
from bot.i18n import _

import discord
from discord.ext import commands

from bot.chess.chess import Chess
from bot.chess.puzzle import Puzzle


def get_current_game(func):
    """
    Decorates a command that requires current user's games

    Use this decorator if your chess command requires the author's games, requesting
    addiotional optional command argument for author's oponent when playing multiple
    games at once.

    This will change the decorated command signature, removing the passing game
    parameter so that discord.py doesn't see it, thus keeping it from being a command
    argument. It will also add user2 command argument to the function signature.
    
    Because decorated commands will have an adiotional optional argument (as explained
    above), it is advisable to include this behaviour in the decorated command's doc.
    This decorator will try to format decorated funtions's docstring with a `user2_doc`
    key. As such, in order to properly document this changed behaviour, simply incluse
    `{user2_doc}` into the function's doc where appropriate.
    """
    async def function_wrapper(this, ctx, *args, user2, **kwargs):
        try:
            game = this.chess_bot.find_current_game(ctx.author, user2)
        except Exception as e:
            await ctx.send(str(e))
            return
        
        func_args = [this, ctx] + list(args)
        await func(*func_args, game=game, **kwargs)
    
    command_signature = inspect.signature(func)
    command_signature_parameters = command_signature.parameters.copy()
    del command_signature_parameters['game']
    command_signature_parameters.update({'user2': inspect.Parameter(
        'user2',
        inspect.Parameter.KEYWORD_ONLY,
        default=None,
        annotation=discord.User
    )})

    function_wrapper.__name__ = func.__name__
    function_wrapper.__doc__ = func.__doc__.format(
        user2_doc=_("Identify your opponent in case you are playing multiple games at once.")
    )
    function_wrapper.__signature__ = command_signature.replace(
        parameters=command_signature_parameters.values())
    return function_wrapper


class ChessCog(commands.Cog):
    """
    Xadrez
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
        Inicie uma nova partida de xadrez com alguém

        Passe o usuário contra o qual deseja jogar para começar uma partida. \
        Se quiser personalizar as cores do tabuleiro, passe o nome da cor que deseja usar \
        (opções válidas: `blue`, `purple`, `green`, `red`, `gray` e `wood`).
        """
        bot_info = await self.client.application_info()
        if user2.id == bot_info.id:
            return await ctx.send(
                _("In order to play a game against the bot, use the command `{prefix}xadrez_bot`")
                .format(prefix=self.client.command_prefix)
            )
        result = self.chess_bot.new_game(ctx.author, user2, color_schema=color_schema)
        await ctx.send(result)

    @commands.command(aliases=['xpve', 'xcpu', 'xb'])
    async def xadrez_bot(self, ctx, cpu_level: int, color_schema=None):
        """
        Inicie uma nova partida de xadrez contra o bot

        Passe o nível de dificuldade que desejar (de 0 a 20). \
        Se quiser personalizar as cores do tabuleiro, passe o nome da cor que deseja usar \
        (opções válidas: `blue`, `purple`, `green`, `red`, `gray` e `wood`).
        """
        bot_info = await self.client.application_info()
        result = self.chess_bot.new_game(
            ctx.author, bot_info, cpu_level=cpu_level, color_schema=color_schema)
        await ctx.send(result)

    @commands.command(aliases=['xj'])
    @get_current_game
    async def xadrez_jogar(self, ctx, move, *, game):
        """
        Faça uma jogada em sua partida atual

        Use anotação SAN ou UCI. Movimentos inválidos ou ambíguos são rejeitados. {user2_doc}
        """
        await ctx.trigger_typing()
        result, board_png_bytes = await self.chess_bot.make_move(game, move)
        await ctx.send(result)
        if board_png_bytes:
            await ctx.send(file=discord.File(board_png_bytes, 'board.png'))
            await self.chess_bot.save_games()

            evaluation = await self.chess_bot.eval_last_move(game)
            if evaluation["blunder"]:
                await ctx.send("👀")
            elif evaluation["mate_in"] and evaluation["mate_in"] in range(1, 4):
                sheev_msgs = [
                    _("DEW IT!"),
                    _("Kill him! Kill him now!"),
                    _("Good, {username}, good!").format(username=game.current_player.name)
                ]
                await ctx.send(sheev_msgs[evaluation["mate_in"] - 1])

    @commands.command(aliases=['xa'])
    @get_current_game
    async def xadrez_abandonar(self, ctx, *, game):
        """
        Abandone a partida atual

        {user2_doc}
        """
        await ctx.trigger_typing()
        result, board_png_bytes = await self.chess_bot.resign(game)
        await ctx.send(result)
        if board_png_bytes:
            await ctx.send(file=discord.File(board_png_bytes, 'board.png'))
            await self.chess_bot.save_games()

    @commands.command(aliases=['xpgn'])
    @get_current_game
    async def xadrez_pgn(self, ctx, *, user2: discord.User=None, game):
        """
        Gera o PGN da partida atual

        {user2_doc}
        """
        result = self.chess_bot.generate_pgn(game)
        await ctx.send(result)

    @commands.command(aliases=['xpos'])
    @get_current_game
    async def xadrez_posicao(self, ctx, *, game):
        """
        Mostra a posição atual da partida em andamento

        {user2_doc}
        """
        image = self.chess_bot.build_png_board(game)
        await ctx.send(file=discord.File(image, 'board.png'))

    @commands.command(aliases=['xt', 'xadrez_jogos'])
    async def xadrez_todos(self, ctx, page: int=0):
        """
        Veja todas as partidas que estão sendo jogadas agora
        """
        await ctx.trigger_typing()
        png_bytes = await self.chess_bot.get_all_boards_png(page)
        if not png_bytes:
            # await ctx.send(_("Nenhuma partida está sendo jogada... ☹️ Inicie uma com `cp!xadrez_novo`."))
            await ctx.send(
                _("No game is being played currently... ☹️ Start a new one with `{prefix}!xadrez_novo`")
                .format(prefix=self.client.command_prefix)
            )
        else:
            await ctx.send(file=discord.File(png_bytes, 'boards.png'))

    @commands.command(aliases=['xgif'])
    async def xadrez_gif(self, ctx, game_id: str, move_number: int, *moves):
        """
        Exibe um GIF animado com uma variante fornecida para o jogo em questão, a partir do lance fornecido

        É necessário passar o jogo em questão, identificado com seu UUID, e o número do lance a partir do qual \
            a sequência fornecida se inicia, que deve ser uma sequência de lances em UCI ou SAN separados por espaço.

        Exemplo de uso: `xgif f63e5e4f-dd94-4439-a283-33a1c1a065a0 11 Nxf5 Qxf5 Qxf5 gxf5`
        """
        await ctx.trigger_typing()
        chess_game = await self.chess_bot.get_game_by_id(game_id)
        if not chess_game:
            return await ctx.send(_("Game not found"))
        gif_bytes = await self.chess_bot.build_animated_sequence_gif(chess_game, move_number, moves)
        if not gif_bytes:
            return await ctx.send(_("Invalid move for the given sequence"))
        return await ctx.send(file=discord.File(gif_bytes, 'variation.gif'))

    @commands.command(aliases=['xp'])
    async def xadrez_puzzle(self, ctx, puzzle_id=None, move=''):
        """
        Pratique um puzzle de xadrez

        Envie o comando sem argumentos para um novo puzzle. Para tentar uma jogada em um puzzle, \
        envie o ID do puzzle como primeiro argumento e a jogada como segundo.

        Exemplo de novo puzzle: `xadrez_puzzle`
        Exemplo de jogada em puzzle existente: `xadrez_puzzle 557b7aa7e13823b82b9bc1e9 Qa2`
        """
        await ctx.trigger_typing()
        if not puzzle_id:
            puzzle_dict = await self.puzzle_bot.get_random_puzzle()
            if 'error' in puzzle_dict:
                return await ctx.send(
                    f'{_("There has been an error when trying to fetch a new puzzle")}: {puzzle_dict["error"]}')
            puzzle = self.puzzle_bot.build_puzzle(puzzle_dict)
            if 'error' in puzzle:
                return await ctx.send(
                    f'{_("There has been an error when trying to build a new puzzle")}: {puzzle["error"]}')
            return await ctx.send(puzzle["id"], file=discord.File(self.chess_bot.build_png_board(puzzle["game"]), 'puzzle.png'))
        
        puzzle_result = self.puzzle_bot.validate_puzzle_move(puzzle_id, move)
        if isinstance(puzzle_result, str):
            return await ctx.send(puzzle_result)
        
        if puzzle_result:
            if self.puzzle_bot.is_puzzle_over(puzzle_id):
                return await ctx.send(_("Good job, puzzle solved 👍"))
        if puzzle_result or move == '':
            return await ctx.send(file=discord.File(
                self.chess_bot.build_png_board(self.puzzle_bot.puzzles[puzzle_id]["game"]), 'puzzle.png'))
        
        return await ctx.send(_("Wrong answer"))
