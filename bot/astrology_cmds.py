import logging

import discord
from discord.ext import commands
from discord_slash import cog_ext
from discord_slash.utils.manage_commands import create_option

from bot.astrology.astrology_chart import AstrologyChart
from bot.astrology.exception import AstrologyInvalidInput
from bot.utils import i


class AstrologyCog(commands.Cog):
    """
    Astrologia
    """

    def __init__(self, client):
        self.client = client
        self.astrology_bot = AstrologyChart()

    @cog_ext.cog_slash(
        name="mapa_astral",
        description="Visualize seu mapa astral criado via DM",
        guild_ids=[297129074692980737]
    )
    async def show_astrology_chart(self, ctx):
        user_chart = await self.astrology_bot.get_user_chart(ctx.author.id)
        if not user_chart:
            return await ctx.send(
                i(ctx, 'You have not yet created your astrology chart. In order to do so, send this command to my DM 😁'))
        return await self.send_astrology_triad(ctx, user_chart)
    
    @commands.command()
    @commands.dm_only()
    async def mapa_astral(self, ctx, date, time, *, city_name):
        """
        Visualize ou crie via DM seu mapa astral

        Para criar seu mapa astral, envie esse comando em DM para o bot informando \
            a data, hora e local de seu nascimento da seguinte forma: \
            `YYYY/mm/dd HH:MM Nome da cidade`.

        Exemplo de uso para criação de mapa astral: `mapa_astral 2000/15/01 12:00 Brasília`
        """
        try:
            await ctx.trigger_typing()
            chart = await self.astrology_bot.calc_chart(ctx.author.id, date, time, city_name)
            await self.astrology_bot.save_chart(ctx.author.id, chart)
        except AstrologyInvalidInput as e:
            return await ctx.send(i(ctx, e.message))
        except Exception as e:
            logging.warning(e, exc_info=True)
            return await ctx.send(
                i(ctx, 'There has been a momentary failure. Please try again in a few moments. If this error persists, then this might be a bug 😬')
            )
        await self.send_astrology_triad(ctx, chart)

    async def send_astrology_triad(self, ctx, chart):
        sign = self.astrology_bot.get_sun_sign(chart)
        asc = self.astrology_bot.get_asc_sign(chart)
        moon = self.astrology_bot.get_moon_sign(chart)

        embed = discord.Embed(
            title=i(ctx, 'Your astrology chart'),
            description=i(ctx, 'Your astrology triad'),
            colour=discord.Color.blurple()
        )
        embed.add_field(name=i(ctx, 'Solar sign'), value=sign)
        embed.add_field(name=i(ctx, 'Ascending sign'), value=asc)
        embed.add_field(name=i(ctx, 'Moon sign'), value=moon)
        await ctx.send(embed=embed)
