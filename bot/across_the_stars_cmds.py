import os
from bot.i18n import _

import discord
from discord.ext import commands

from bot.across_the_stars.planets import Planets


class AcrossTheStarsCmds(commands.Cog):
    """
    Jogo Across The Stars
    """
    def __init__(self, client):
        self.client = client
        self.planets = Planets()

    @commands.command(aliases=['planets'])
    async def planetas(self, ctx, *, region=None):
        """
        Lista todos os planetas disponíveis da região fornecida
        """
        discord_file = discord.File(
            os.path.join('bot', 'images', 'arnaldo-o-hutt.gif'), 'hutt.gif')

        planets = await self.planets.list_of_planets(region=region)

        embed = discord.Embed(
            title=_("Arnaldo's Emporium"),
            description=_("Become a planet's senator"),
            colour=discord.Color.green()
        )
        embed.set_thumbnail(url="attachment://hutt.gif")
        for planet in planets:
            embed.add_field(
                name=planet.name,
                value=f'{_("Price")}: {planet.price}\n{_("Region")}: {planet.region}\n'\
                    f'{_("Climate")}: {planet.climate}\n{_("Circuference")}: {planet.circuference}'
            )

        await ctx.reply(embed=embed, file=discord_file, mention_author=False)
