from enum import Enum
import inspect
import logging

import discord
from discord import app_commands

from bot.chess.chess import Chess
from bot.chess.exceptions import ChessException, MultipleGamesAtOnce
from bot.chess.puzzle import Puzzle
from bot.discord_helpers import i


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
    async def function_wrapper(this, interaction, *args, **kwargs):
        try:
            user = args[-1] if args else kwargs.get("user", None)
            game = this.chess_bot.find_current_game(interaction.user, user)
        except MultipleGamesAtOnce as e:
            return await interaction.response.send_message(i(interaction, e.message).format(number_of_games=e.number_of_games))
        except ChessException as e:
            return await interaction.response.send_message(i(interaction, e.message))
        
        func_args = [this, interaction] + list(args)
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
    function_wrapper.__qualname__ = func.__qualname__
    function_wrapper.__doc__ = func.__doc__.format(
        user2_doc="Informe o seu oponente caso esteja disputando múltiplas partidas ao mesmo tempo."
    )
    function_wrapper.__signature__ = command_signature.replace(
        parameters=command_signature_parameters.values())
    return function_wrapper


class ChessBoardColors(Enum):
    blue = 1
    purple = 2
    green = 3
    red = 4
    gray = 5
    wood = 6


class ChessCmds(app_commands.Group):
    """
    Xadrez
    """

    def __init__(self, client):
        self.client = client
        self.client.add_listener(self.on_connect)
        self.chess_bot = Chess()
        self.puzzle_bot = Puzzle()
        super().__init__(name='xadrez')

    async def on_connect(self):
        await self.chess_bot.load_games()
        logging.info(f'Successfully loaded {len(self.chess_bot.games)} active chess games')
    
    @app_commands.command(
        name="novo",
        description="Inicie uma nova partida de xadrez com alguém"
    )
    @app_commands.describe(user='Usuário contra quem quer jogar', color_schema='Cores do tabuleiro')
    async def new_game_pvp(self, interaction: discord.Interaction, user: discord.User, color_schema: ChessBoardColors=None):
        """
        Inicie uma nova partida de xadrez com alguém

        Passe o usuário contra o qual deseja jogar para começar uma partida. \
        Se quiser personalizar as cores do tabuleiro, passe o nome da cor que deseja usar \
        (opções válidas: `blue`, `purple`, `green`, `red`, `gray` e `wood`).
        """
        bot_info = await self.client.application_info()
        if user.id == bot_info.id:
            return await interaction.response.send_message(
                i(interaction, "In order to play a game against the bot, use the command `{prefix}xadrez_bot`")
                .format(prefix=self.client.command_prefix)
            )
        try:
            game = self.chess_bot.new_game(interaction.user, user, color_schema=color_schema.name if color_schema else None)
            await interaction.response.send_message(i(interaction, 'Game started! {}, play your move').format(game.player1.name))
        except ChessException as e:
            await interaction.response.send_message(i(interaction, e.message))

    @app_commands.command(
        name="bot",
        description="Inicie uma nova partida de xadrez contra o bot"
    )
    @app_commands.describe(cpu_level='Nível de dificuldate (0 a 20)', color_schema='Cores do tabuleiro')
    async def new_game_pve(self, interaction: discord.Interaction, cpu_level: int, color_schema: ChessBoardColors=None):
        """
        Inicie uma nova partida de xadrez contra o bot

        Passe o nível de dificuldade que desejar (de 0 a 20). \
        Se quiser personalizar as cores do tabuleiro, passe o nome da cor que deseja usar \
        (opções válidas: `blue`, `purple`, `green`, `red`, `gray` e `wood`).
        """
        bot_info = await self.client.application_info()
        try:
            game = self.chess_bot.new_game(
                interaction.user, bot_info, cpu_level=cpu_level, color_schema=color_schema.name if color_schema else None)
            await interaction.response.send_message(i(interaction, 'Game started! {}, play your move').format(game.player1.name))
        except ChessException as e:
            await interaction.response.send_message(i(interaction, e.message))

    @app_commands.command(
        name="jogar",
        description="Faça uma jogada em sua partida atual"
    )
    @app_commands.describe(move='Use anotação SAN ou UCI', user='Informe o seu oponente caso esteja disputando múltiplas partidas ao mesmo tempo')
    @get_current_game
    async def play_move(self, interaction: discord.Interaction, move: str, *, game):
        """
        Faça uma jogada em sua partida atual

        Use anotação SAN ou UCI. Movimentos inválidos ou ambíguos são rejeitados. {user2_doc}
        """
        await interaction.response.defer()
        async with interaction.channel.typing():
            try:
                game = await self.chess_bot.make_move(game, move)
            except ChessException as e:
                return await interaction.followup.send(i(interaction, e.message))
            
            if self.chess_bot.is_game_over(game):
                pgn = self.chess_bot.generate_pgn(game)
                message = f'{i(interaction, "Game over!")}\n\n{pgn}'
            else:
                message = i(interaction, "That's your turn now, {}").format(game.current_player.name)
            
            board_png_bytes = self.chess_bot.build_png_board(game)
            await interaction.followup.send(
                content=message,
                file=discord.File(board_png_bytes, 'board.png')
            )

        evaluation = await self.chess_bot.eval_last_move(game)
        if evaluation["blunder"]:
            await interaction.channel.send("👀")
        elif evaluation["mate_in"] and evaluation["mate_in"] in range(1, 4):
            sheev_msgs = [
                i(interaction, "DEW IT!"),
                i(interaction, "Kill him! Kill him now!"),
                i(interaction, "Good, {username}, good!").format(username=game.current_player.name)
            ]
            await interaction.channel.send(sheev_msgs[evaluation["mate_in"] - 1])

    @app_commands.command(
        name="abandonar",
        description="Abandone a partida atual"
    )
    @app_commands.describe(user='Informe o seu oponente caso esteja disputando múltiplas partidas ao mesmo tempo')
    @get_current_game
    async def resign(self, interaction: discord.Interaction, *, game):
        """
        Abandone a partida atual

        {user2_doc}
        """
        await interaction.response.defer()
        async with interaction.channel.typing():
            game = await self.chess_bot.resign(game)
            pgn = self.chess_bot.generate_pgn(game)
            board_png_bytes = self.chess_bot.build_png_board(game)
            await interaction.followup.send(
                content=i(interaction, '{} has abandoned the game!').format(game.current_player.name)+f'\n{pgn}',
                file=discord.File(board_png_bytes, 'board.png')
            )

    @app_commands.command(
        name="pgn",
        description="Gera o PGN da partida atual"
    )
    @app_commands.describe(user='Informe o seu oponente caso esteja disputando múltiplas partidas ao mesmo tempo')
    @get_current_game
    async def get_game_pgn(self, interaction: discord.Interaction, *, game):
        """
        Gera o PGN da partida atual

        {user2_doc}
        """
        await interaction.response.defer()
        async with interaction.channel.typing():
            result = self.chess_bot.generate_pgn(game)
            await interaction.followup.send(result)

    @app_commands.command(
        name="posicao",
        description="Mostra a posição atual da partida em andamento"
    )
    @app_commands.describe(user='Informe o seu oponente caso esteja disputando múltiplas partidas ao mesmo tempo')
    @get_current_game
    async def get_game_position(self, interaction: discord.Interaction, *, game):
        """
        Mostra a posição atual da partida em andamento

        {user2_doc}
        """
        await interaction.response.defer()
        async with interaction.channel.typing():
            image = self.chess_bot.build_png_board(game)
            await interaction.followup.send(file=discord.File(image, 'board.png'))

    @app_commands.command(
        name="todos",
        description="Veja todas as partidas que estão sendo jogadas agora"
    )
    @app_commands.describe(page='Página')
    async def all_current_games(self, interaction: discord.Interaction, page: int=0):
        """
        Veja todas as partidas que estão sendo jogadas agora
        """
        await interaction.response.defer()
        async with interaction.channel.typing():
            png_bytes = await self.chess_bot.get_all_boards_png(page)
            if not png_bytes:
                await interaction.followup.send(
                    i(interaction, "No game is being played currently... ☹️ Start a new one with `{prefix}!xadrez_novo`")
                    .format(prefix=self.client.command_prefix)
                )
            else:
                await interaction.followup.send(file=discord.File(png_bytes, 'boards.png'))

    @app_commands.command(
        name="gif",
        description="Exibe um GIF animado com uma variante fornecida para o jogo em questão, a partir do lance fornecido"
    )
    @app_commands.describe(game_id='UUID da partida', move_number='Número do lance', moves='Jogadas')
    async def make_animated_gif(self, interaction: discord.Interaction, game_id: str, move_number: int, moves: str):
        """
        Exibe um GIF animado com uma variante fornecida para o jogo em questão, a partir do lance fornecido

        É necessário passar o jogo em questão, identificado com seu UUID, e o número do lance a partir do qual \
            a sequência fornecida se inicia, que deve ser uma sequência de lances em UCI ou SAN separados por espaço.

        Exemplo de uso: `xgif f63e5e4f-dd94-4439-a283-33a1c1a065a0 11 Nxf5 Qxf5 Qxf5 gxf5`
        """
        await interaction.response.defer()
        async with interaction.channel.typing():
            chess_game = await self.chess_bot.get_game_by_id(game_id)
            if not chess_game:
                return await interaction.followup.send(i(interaction, "Game not found"))
            
            gif_bytes = await self.chess_bot.build_animated_sequence_gif(
                chess_game, move_number, moves.split(" "))
            if not gif_bytes:
                return await interaction.followup.send(i(interaction, "Invalid move for the given sequence"))
            return await interaction.followup.send(file=discord.File(gif_bytes, 'variation.gif'))

    @app_commands.command(
        name="puzzle",
        description="Pratique um puzzle de xadrez"
    )
    @app_commands.describe(puzzle_id='ID do puzzle', move='Lance')
    async def xadrez_puzzle(self, interaction: discord.Interaction, puzzle_id: str=None, move: str=''):
        """
        Pratique um puzzle de xadrez

        Envie o comando sem argumentos para um novo puzzle. Para tentar uma jogada em um puzzle, \
        envie o ID do puzzle como primeiro argumento e a jogada como segundo.

        Exemplo de novo puzzle: `xadrez_puzzle`
        Exemplo de jogada em puzzle existente: `xadrez_puzzle 557b7aa7e13823b82b9bc1e9 Qa2`
        """
        await interaction.response.defer()
        if not puzzle_id:
            puzzle_dict = await self.puzzle_bot.get_random_puzzle()
            if 'error' in puzzle_dict:
                return await interaction.followup.send(
                    f'{i(interaction, "There has been an error when trying to fetch a new puzzle")}: {puzzle_dict["error"]}')
            puzzle = self.puzzle_bot.build_puzzle(puzzle_dict)
            if 'error' in puzzle:
                return await interaction.followup.send(
                    f'{i(interaction, "There has been an error when trying to build a new puzzle")}: {puzzle["error"]}')
            return await interaction.followup.send(puzzle["id"], file=discord.File(self.chess_bot.build_png_board(puzzle["game"]), 'puzzle.png'))
        
        try:
            puzzle_result = self.puzzle_bot.validate_puzzle_move(puzzle_id, move)
        except ChessException as e:
            return await interaction.followup.send(i(interaction, e.message))
        
        if puzzle_result:
            if self.puzzle_bot.is_puzzle_over(puzzle_id):
                return await interaction.followup.send(i(interaction, "Good job, puzzle solved 👍"))
        if puzzle_result or move == '':
            return await interaction.followup.send(file=discord.File(
                self.chess_bot.build_png_board(
                    self.puzzle_bot.puzzles[puzzle_id]["game"]), 'puzzle.png')
            )
        
        return await interaction.followup.send(i(interaction, "Wrong answer"))
