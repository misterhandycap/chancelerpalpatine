import discord
from discord.ext import commands

from bot.akinator.akinator_game import AkinatorGame


class AkinatorCog(commands.Cog):
    """
    Comandos para jogos com Akinator
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
        """
        await ctx.trigger_typing()
        game, question = await self.akinator_bot.new_game(ctx.author)
        await ctx.send("Jogo iniciado. Responda reagindo às perguntas do bot.")
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
        
        await reaction.message.channel.trigger_typing()
        answer = [k for k, v in self.emoji_answers.items() if v == emoji][0]
        result = await self.akinator_bot.answer_question(game, answer)
        if isinstance(result, str):
            await self.send_embed(result, user, reaction.message.channel)
        else:
            embed = discord.Embed(
                title=f'{user.name} pensou em {result.get("name")}',
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
