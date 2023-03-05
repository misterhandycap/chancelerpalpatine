import logging

import discord
from discord import app_commands

from bot.astrology.astrology_chart import AstrologyChart
from bot.astrology.exception import AstrologyInvalidInput
from bot.utils import dm_only, i


class AstrologyCmds(app_commands.Group):
    """
    Astrologia
    """

    def __init__(self, client):
        self.client = client
        self.astrology_bot = AstrologyChart()
        super().__init__(name='astrologia')

    @app_commands.command(
        name="mapa_astral",
        description="Visualize seu mapa astral criado via DM"
    )
    async def show_astrology_chart(self, interaction: discord.Interaction):
        user_chart = await self.astrology_bot.get_user_chart(interaction.user.id)
        if not user_chart:
            return await interaction.response.send_message(
                i(interaction, 'You have not yet created your astrology chart. In order to do so, send this command to my DM 😁'))
        return await self.send_astrology_triad(interaction, user_chart)
    
    @app_commands.command(
        name='criar',
        description='Visualize ou crie via DM seu mapa astral'
    )
    @app_commands.describe(date='Data no formato YYYY/mm/dd', time='Horário no formato HH:MM', city_name='Cidade')
    @app_commands.check(dm_only)
    async def mapa_astral(self, interaction: discord.Interaction, date: str, time: str, city_name: str):
        """
        Visualize ou crie via DM seu mapa astral

        Para criar seu mapa astral, envie esse comando em DM para o bot informando \
            a data, hora e local de seu nascimento da seguinte forma: \
            `YYYY/mm/dd HH:MM Nome da cidade`.

        Exemplo de uso para criação de mapa astral: `mapa_astral 2000/15/01 12:00 Brasília`
        """
        try:
            chart = await self.astrology_bot.calc_chart(interaction.user.id, date, time, city_name)
            await self.astrology_bot.save_chart(interaction.user.id, chart)
        except AstrologyInvalidInput as e:
            return await interaction.response.send_message(i(interaction, e.response.message_send_message))
        except Exception as e:
            logging.warning(e, exc_info=True)
            return await interaction.response.send_message(
                i(interaction, 'There has been a momentary failure. Please try again in a few moments. If this error persists, then this might be a bug 😬')
            )
        await self.send_astrology_triad(interaction, chart)
        
    @mapa_astral.error
    async def handle_errors(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.errors.CheckFailure):
            await interaction.response.send_message(
                i(interaction, 'Command only available through DM'))

    async def send_astrology_triad(self, interaction, chart):
        sign = self.astrology_bot.get_sun_sign(chart)
        asc = self.astrology_bot.get_asc_sign(chart)
        moon = self.astrology_bot.get_moon_sign(chart)

        embed = discord.Embed(
            title=i(interaction, 'Your astrology chart'),
            description=i(interaction, 'Your astrology triad'),
            colour=discord.Color.blurple()
        )
        embed.add_field(name=i(interaction, 'Solar sign'), value=sign)
        embed.add_field(name=i(interaction, 'Ascending sign'), value=asc)
        embed.add_field(name=i(interaction, 'Moon sign'), value=moon)
        await interaction.response.send_message(embed=embed)
