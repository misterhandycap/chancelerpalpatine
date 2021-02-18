from bot.across_the_stars.planets import Planets
import discord
from discord.ext import commands


class AcrossTheStarsCmds(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.planets = Planets()

    @commands.command(aliases=['planets'])
    async def planetas(self, ctx, *, args):
        planets = await self.planets.list_of_planets(region=args)
        print(planets)
        await ctx.reply('aoba'
        mention_author=False)
