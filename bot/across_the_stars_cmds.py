import os

import discord
from discord import app_commands

from bot.across_the_stars.planets import Planets
from bot.discord_helpers import i


class AcrossTheStarsCmds(app_commands.Group):
    """
    Jogo Across The Stars
    """
    def __init__(self, client):
        self.client = client
        self.planets = Planets()
        super().__init__(name='across_the_stars')

    @app_commands.command(
        name="planetas",
        description="Lista todos os planetas disponíveis da região fornecida"
    )
    @app_commands.describe(region='Região galáctica')
    async def list_planets(self, interaction: discord.Interaction, region: str=None):
        """
        Lista todos os planetas disponíveis da região fornecida
        """
        discord_file = discord.File(
            os.path.join('bot', 'images', 'arnaldo-o-hutt.gif'), 'hutt.gif')

        planets = await self.planets.list_of_planets(region=region)

        embed = discord.Embed(
            title=i(interaction, "Arnaldo's Emporium"),
            description=i(interaction, "Become a planet's senator"),
            colour=discord.Color.green()
        )
        embed.set_thumbnail(url="attachment://hutt.gif")
        for planet in planets:
            embed.add_field(
                name=planet.name,
                value=f'{i(interaction, "Price")}: {planet.price}\n{i(interaction, "Region")}: {planet.region}\n'\
                    f'{i(interaction, "Climate")}: {planet.climate}\n{i(interaction, "Circuference")}: {planet.circuference}'
            )

        await interaction.response.send_message(embed=embed, file=discord_file)
