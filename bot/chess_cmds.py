import inspect
import logging

import discord
from discord.ext import commands
from discord_slash import cog_ext
from discord_slash.utils.manage_commands import create_option

from bot.chess.chess import Chess
from bot.chess.exceptions import ChessException, MultipleGamesAtOnce
from bot.chess.puzzle import Puzzle
from bot.utils import i


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
    async def function_wrapper(this, ctx, *args, **kwargs):
        try:
            user = args[-1] if args else kwargs.get("user", None)
            game = this.chess_bot.find_current_game(ctx.author, user)
        except MultipleGamesAtOnce as e:
            return await ctx.send(i(ctx, e.message).format(number_of_games=e.number_of_games))
        except ChessException as e:
            return await ctx.send(i(ctx, e.message))
        
        func_args = [this, ctx] + list(args)
        if 'user' in kwargs:
            del kwargs["user"]
        await func(*func_args, game=game, **kwargs)
    
    command_signature = inspect.signature(func)
    command_signature_parameters = command_signature.parameters.copy()
    del command_signature_parameters['game']
    command_signature_parameters.update({'user': inspect.Parameter(
        'user',
        inspect.Parameter.POSITIONAL_OR_KEYWORD,
        default=None,
        annotation=discord.User
    )})

    function_wrapper.__name__ = func.__name__
    function_wrapper.__doc__ = func.__doc__.format(
        user2_doc="Informe o seu oponente caso esteja disputando múltiplas partidas ao mesmo tempo."
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
    
    @cog_ext.cog_slash(
        name="xadrez_novo",
        description="Inicie uma nova partida de xadrez com alguém",
        options=[
            create_option(name="user", description="Usuário contra quem quer jogar", option_type=6, required=True),
            create_option(
                name="color_schema",
                description="Cores do tabuleiro",
                option_type=3,
                required=False,
                choices=["blue", "purple", "green", "red", "gray", "wood"]
            ),
        ],
        guild_ids=[297129074692980737]
    )
    async def new_game_pvp(self, ctx, user: discord.User, color_schema=None):
        """
        Inicie uma nova partida de xadrez com alguém

        Passe o usuário contra o qual deseja jogar para começar uma partida. \
        Se quiser personalizar as cores do tabuleiro, passe o nome da cor que deseja usar \
        (opções válidas: `blue`, `purple`, `green`, `red`, `gray` e `wood`).
        """
        bot_info = await self.client.application_info()
        if user.id == bot_info.id:
            return await ctx.send(
                i(ctx, "In order to play a game against the bot, use the command `{prefix}xadrez_bot`")
                .format(prefix=self.client.command_prefix)
            )
        try:
            game = self.chess_bot.new_game(ctx.author, user, color_schema=color_schema)
            await ctx.send(i(ctx, 'Game started! {}, play your move').format(game.player1.name))
        except ChessException as e:
            await ctx.send(i(ctx, e.message))

    @cog_ext.cog_slash(
        name="xadrez_bot",
        description="Inicie uma nova partida de xadrez contra o bot",
        options=[
            create_option(name="cpu_level", description="Nível de dificuldade", option_type=4, required=True),
            create_option(
                name="color_schema",
                description="Cores do tabuleiro",
                option_type=3,
                required=False,
                choices=["blue", "purple", "green", "red", "gray", "wood"]
            ),
        ],
        guild_ids=[297129074692980737]
    )
    async def new_game_pve(self, ctx, cpu_level: int, color_schema=None):
        """
        Inicie uma nova partida de xadrez contra o bot

        Passe o nível de dificuldade que desejar (de 0 a 20). \
        Se quiser personalizar as cores do tabuleiro, passe o nome da cor que deseja usar \
        (opções válidas: `blue`, `purple`, `green`, `red`, `gray` e `wood`).
        """
        bot_info = await self.client.application_info()
        try:
            game = self.chess_bot.new_game(
                ctx.author, bot_info, cpu_level=cpu_level, color_schema=color_schema)
            await ctx.send(i(ctx, 'Game started! {}, play your move').format(game.player1.name))
        except ChessException as e:
            await ctx.send(i(ctx, e.message))

    @cog_ext.cog_slash(
        name="xadrez_jogar",
        description="Faça uma jogada em sua partida atual",
        options=[
            create_option(name="move", description="Use anotação SAN ou UCI", option_type=3, required=True),
            create_option(
                name="user",
                description="Informe o seu oponente caso esteja disputando múltiplas partidas ao mesmo tempo",
                option_type=6,
                required=False
            ),
        ],
        guild_ids=[297129074692980737]
    )
    @get_current_game
    async def play_move(self, ctx, move, *, game):
        """
        Faça uma jogada em sua partida atual

        Use anotação SAN ou UCI. Movimentos inválidos ou ambíguos são rejeitados. {user2_doc}
        """
        await ctx.defer()
        async with ctx.channel.typing():
            try:
                game = await self.chess_bot.make_move(game, move)
            except ChessException as e:
                return await ctx.send(i(ctx, e.message))
            
            if self.chess_bot.is_game_over(game):
                pgn = self.chess_bot.generate_pgn(game)
                message = f'{i(ctx, "Game over!")}\n\n{pgn}'
            else:
                message = i(ctx, "That's your turn now, {}").format(game.current_player.name)
            
            board_png_bytes = self.chess_bot.build_png_board(game)
            await ctx.send(
                content=message,
                file=discord.File(board_png_bytes, 'board.png')
            )

        evaluation = await self.chess_bot.eval_last_move(game)
        if evaluation["blunder"]:
            await ctx.send("👀")
        elif evaluation["mate_in"] and evaluation["mate_in"] in range(1, 4):
            sheev_msgs = [
                i(ctx, "DEW IT!"),
                i(ctx, "Kill him! Kill him now!"),
                i(ctx, "Good, {username}, good!").format(username=game.current_player.name)
            ]
            await ctx.send(sheev_msgs[evaluation["mate_in"] - 1])

    @cog_ext.cog_slash(
        name="xadrez_abandonar",
        description="Abandone a partida atual",
        options=[
            create_option(
                name="user",
                description="Informe o seu oponente caso esteja disputando múltiplas partidas ao mesmo tempo",
                option_type=6,
                required=False
            ),
        ],
        guild_ids=[297129074692980737]
    )
    @get_current_game
    async def resign(self, ctx, *, game):
        """
        Abandone a partida atual

        {user2_doc}
        """
        await ctx.defer()
        async with ctx.channel.typing():
            game = await self.chess_bot.resign(game)
            pgn = self.chess_bot.generate_pgn(game)
            board_png_bytes = self.chess_bot.build_png_board(game)
            await ctx.send(
                content=i(ctx, '{} has abandoned the game!').format(game.current_player.name)+f'\n{pgn}',
                file=discord.File(board_png_bytes, 'board.png')
            )

    @cog_ext.cog_slash(
        name="xadrez_pgn",
        description="Gera o PGN da partida atual",
        options=[
            create_option(
                name="user",
                description="Informe o seu oponente caso esteja disputando múltiplas partidas ao mesmo tempo",
                option_type=6,
                required=False
            ),
        ],
        guild_ids=[297129074692980737]
    )
    @get_current_game
    async def get_game_pgn(self, ctx, *, game):
        """
        Gera o PGN da partida atual

        {user2_doc}
        """
        await ctx.defer()
        async with ctx.channel.typing():
            result = self.chess_bot.generate_pgn(game)
            await ctx.send(result)

    @cog_ext.cog_slash(
        name="xadrez_posicao",
        description="Mostra a posição atual da partida em andamento",
        options=[
            create_option(
                name="user",
                description="Informe o seu oponente caso esteja disputando múltiplas partidas ao mesmo tempo",
                option_type=6,
                required=False
            ),
        ],
        guild_ids=[297129074692980737]
    )
    @get_current_game
    async def get_game_position(self, ctx, *, game):
        """
        Mostra a posição atual da partida em andamento

        {user2_doc}
        """
        await ctx.defer()
        async with ctx.channel.typing():
            image = self.chess_bot.build_png_board(game)
            await ctx.send(file=discord.File(image, 'board.png'))

    @cog_ext.cog_slash(
        name="xadrez_todos",
        description="Veja todas as partidas que estão sendo jogadas agora",
        options=[
            create_option(name="page", description="Página", option_type=4, required=False),
        ],
        guild_ids=[297129074692980737]
    )
    async def all_current_games(self, ctx, page: int=0):
        """
        Veja todas as partidas que estão sendo jogadas agora
        """
        await ctx.defer()
        async with ctx.channel.typing():
            png_bytes = await self.chess_bot.get_all_boards_png(page)
            if not png_bytes:
                await ctx.send(
                    i(ctx, "No game is being played currently... ☹️ Start a new one with `{prefix}!xadrez_novo`")
                    .format(prefix=self.client.command_prefix)
                )
            else:
                await ctx.send(file=discord.File(png_bytes, 'boards.png'))

    @cog_ext.cog_slash(
        name="xadrez_gif",
        description="Exibe um GIF animado com uma variante fornecida para o jogo em questão, a partir do lance fornecido",
        options=[
            create_option(name="game_id", description="UUID da partida", option_type=3, required=True),
            create_option(name="move_number", description="Número do lance", option_type=4, required=True),
            create_option(name="moves", description="Jogadas", option_type=3, required=True)
        ],
        guild_ids=[297129074692980737]
    )
    async def make_animated_gif(self, ctx, game_id: str, move_number: int, moves):
        """
        Exibe um GIF animado com uma variante fornecida para o jogo em questão, a partir do lance fornecido

        É necessário passar o jogo em questão, identificado com seu UUID, e o número do lance a partir do qual \
            a sequência fornecida se inicia, que deve ser uma sequência de lances em UCI ou SAN separados por espaço.

        Exemplo de uso: `xgif f63e5e4f-dd94-4439-a283-33a1c1a065a0 11 Nxf5 Qxf5 Qxf5 gxf5`
        """
        await ctx.defer()
        async with ctx.channel.typing():
            chess_game = await self.chess_bot.get_game_by_id(game_id)
            if not chess_game:
                return await ctx.send(i(ctx, "Game not found"))
            
            gif_bytes = await self.chess_bot.build_animated_sequence_gif(
                chess_game, move_number, moves.split(" "))
            if not gif_bytes:
                return await ctx.send(i(ctx, "Invalid move for the given sequence"))
            return await ctx.send(file=discord.File(gif_bytes, 'variation.gif'))

    @cog_ext.cog_slash(
        name="xadrez_puzzle",
        description="Pratique um puzzle de xadrez",
        options=[
            create_option(name="puzzle_id", description="ID do puzzle", option_type=3, required=False),
            create_option(name="move", description="Lance", option_type=3, required=False)
        ],
        guild_ids=[297129074692980737]
    )
    async def xadrez_puzzle(self, ctx, puzzle_id=None, move=''):
        """
        Pratique um puzzle de xadrez

        Envie o comando sem argumentos para um novo puzzle. Para tentar uma jogada em um puzzle, \
        envie o ID do puzzle como primeiro argumento e a jogada como segundo.

        Exemplo de novo puzzle: `xadrez_puzzle`
        Exemplo de jogada em puzzle existente: `xadrez_puzzle 557b7aa7e13823b82b9bc1e9 Qa2`
        """
        await ctx.defer()
        if not puzzle_id:
            puzzle_dict = await self.puzzle_bot.get_random_puzzle()
            if 'error' in puzzle_dict:
                return await ctx.send(
                    f'{i(ctx, "There has been an error when trying to fetch a new puzzle")}: {puzzle_dict["error"]}')
            puzzle = self.puzzle_bot.build_puzzle(puzzle_dict)
            if 'error' in puzzle:
                return await ctx.send(
                    f'{i(ctx, "There has been an error when trying to build a new puzzle")}: {puzzle["error"]}')
            return await ctx.send(puzzle["id"], file=discord.File(self.chess_bot.build_png_board(puzzle["game"]), 'puzzle.png'))
        
        try:
            puzzle_result = self.puzzle_bot.validate_puzzle_move(puzzle_id, move)
        except ChessException as e:
            return await ctx.send(i(ctx, e.message))
        
        if puzzle_result:
            if self.puzzle_bot.is_puzzle_over(puzzle_id):
                return await ctx.send(i(ctx, "Good job, puzzle solved 👍"))
        if puzzle_result or move == '':
            return await ctx.send(file=discord.File(
                self.chess_bot.build_png_board(
                    self.puzzle_bot.puzzles[puzzle_id]["game"]), 'puzzle.png')
            )
        
        return await ctx.send(i(ctx, "Wrong answer"))
