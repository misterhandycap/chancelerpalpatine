import discord
from discord.ext import commands

from bot.akinator.akinator_game import AkinatorGame
from bot.utils import i, get_server_lang


class AkinatorCog(commands.Cog):
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

    def __init__(self, client):
        self.client = client
        self.akinator_bot = AkinatorGame()

    @commands.command(aliases=['an'])
    async def akinator_novo(self, ctx):
        """
        Novo jogo com Akinator

        Responda às perguntas do Akinator através de reações. Legenda:
        ✅: Sim
        🇵: Provavelmente sim
        🤷: Não sei / talvez
        🇺: Provavelmente não
        🚫: Não
        """
        async with ctx.channel.typing():
            lang = get_server_lang(ctx.guild.id)
            game, question = await self.akinator_bot.new_game(ctx.author, lang)
        await ctx.send(i(ctx, "Game started. Answer by reaction to the bot's questions."))
        await self.send_embed(question, ctx.author, ctx)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        game = self.akinator_bot.get_user_game(user)
        if not game or not reaction.message.embeds:
            return
        embed = reaction.message.embeds[0]
        if 'Akinator' not in embed.title:
            return

        emoji = str(reaction)
        if emoji not in self.emoji_answers.values():
            return
        
        answer = [k for k, v in self.emoji_answers.items() if v == emoji][0]
        async with reaction.message.channel.typing():
            result = await self.akinator_bot.answer_question(game, answer)
        if isinstance(result, str):
            await self.send_embed(result, user, reaction.message.channel)
        else:
            embed = discord.Embed(
                title=i(reaction.message, "{username} thought of {name}").format(
                    username=user.name, name=result.get("name")),
                description=result.get('description'),
                colour=discord.Color.blurple()
            )
            embed.set_thumbnail(url=result.get('absolute_picture_path'))
            await reaction.message.channel.send(embed=embed)

    async def send_embed(self, result, user, channel):
        embed = discord.Embed(
            title=f'Akinator: {user.name}',
            description=result,
            colour=discord.Color.blurple()
        )
        message = await channel.send(embed=embed)
        for emoji in self.emoji_answers.values():
            await message.add_reaction(emoji)

    async def cog_command_error(self, ctx, error):
        await ctx.send(i(ctx, "There has been an error with Akinator."))
