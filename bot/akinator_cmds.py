import discord
from discord import app_commands
from discord.ext.commands import Bot

from bot.akinator.akinator_game import AkinatorGame
from bot.discord_helpers import i, get_server_lang


class AkinatorCmds(app_commands.Group):
    """
    Jogos com Akinator
    """

    emoji_answers = {
        'y': '✅',
        'p': '🇵',
        'idk': '🤷',
        'pn': '🇺',
        'n': '🚫'
    }

    def __init__(self, client: Bot):
        self.client: Bot = client
        self.client.add_listener(self.on_reaction_add)
        self.akinator_bot = AkinatorGame()
        super().__init__(name='akinator')

    @app_commands.command(
        name="novo",
        description="Novo jogo com Akinator"
    )
    async def new_game(self, interaction: discord.Interaction):
        """
        Novo jogo com Akinator

        Responda às perguntas do Akinator através de reações. Legenda:
        ✅: Sim
        🇵: Provavelmente sim
        🤷: Não sei / talvez
        🇺: Provavelmente não
        🚫: Não
        """
        await interaction.response.defer()
        async with interaction.channel.typing():
            lang = get_server_lang(interaction.guild_id)
            game, question = await self.akinator_bot.new_game(interaction.user, lang)
        await interaction.followup.send(i(interaction, "Game started. Answer by reaction to the bot's questions."))
        await self.send_embed(question, interaction.user, interaction.channel)

    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.User):
        game = self.akinator_bot.get_user_game(user)
        message = reaction.message
        if not game or not message.embeds or message.author.id != self.client.user.id:
            return
        embed = message.embeds[0]
        if 'Akinator' not in embed.title or game.question.strip() != embed.description.strip():
            return

        emoji = str(reaction)
        if emoji not in self.emoji_answers.values():
            return
        
        answer = [k for k, v in self.emoji_answers.items() if v == emoji][0]
        async with message.channel.typing():
            result = await self.akinator_bot.answer_question(game, answer)
        if isinstance(result, str):
            await self.send_embed(result, user, message.channel)
        else:
            await self.akinator_bot.remove_user_game(user)
            embed = discord.Embed(
                title=i(message, "{username} thought of {name}").format(
                    username=user.name, name=result.get("name")),
                description=result.get('description'),
                colour=discord.Color.blurple()
            )
            embed.set_thumbnail(url=result.get('absolute_picture_path'))
            await message.channel.send(embed=embed)

    async def send_embed(self, result: str, user: discord.User, channel: discord.TextChannel):
        embed = discord.Embed(
            title=f'Akinator: {user.name}',
            description=result,
            colour=discord.Color.blurple()
        )
        message = await channel.send(embed=embed)
        for emoji in self.emoji_answers.values():
            await message.add_reaction(emoji)

    async def cog_command_error(self, interaction, error):
        await interaction.send(i(interaction, "There has been an error with Akinator."))
