from bot.across_the_stars.planets import Planets
import discord
from discord.ext import commands
import os


class AcrossTheStarsCmds(commands.Cog):
    """
    Jogo Across The Stars
    """
    def __init__(self, client):
        self.client = client
        self.planets = Planets()

    @commands.command(aliases=['planets'])
    async def planetas(self, ctx, *, region):
    """
    Lista todos os planetas disponíveis da região fornecida
    """
        discord_file = discord.File(
            os.path.join('bot', 'images', 'arnaldo-o-hutt.gif'), 'hutt.gif')

        planets = await self.planets.list_of_planets(region=args)

        embed = discord.Embed(
            title='Empório do Arnaldo',
            description='Se torne o senador para um planeta',
            colour=discord.Color.green()
        )
        embed.set_thumbnail(url="attachment://hutt.gif")
        for planet in planets:
            embed.add_field(
                name=planet.name,
                value=f'Preço: {planet.price}\nRegião: {planet.region.capitalize()}\nClima: {planet.climate.capitalize()}\nCircunferência: {planet.circuference}'
            )

        await ctx.reply(embed=embed, file=discord_file,
        mention_author=False)