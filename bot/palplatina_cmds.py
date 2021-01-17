from datetime import datetime
import discord
from bot.models.user import User
from discord.ext import commands

class PalplatinaCmds(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()
    async def daily(self, ctx):
        user = await User.get(ctx.message.author.id)
        if not user:
            user = User()
            user.id = ctx.message.author.id
            user.name = ctx.message.author.name
            user.currency = 0
            user.daily_last_collected_at = None

        if user.daily_last_collected_at and (datetime.utcnow() - user.daily_last_collected_at).days < 1:
            await ctx.send('Você já pegou seu daily hoje, tente novamente mais tarde.')
        else:
            user.daily_last_collected_at = datetime.utcnow()
            user.currency += 300
            await ctx.send('Você recebeu 300 palplatinas, faça bom uso.')

        await User.save(user)