import logging

import discord
from discord.ext import commands

from bot.astrology.astrology_chart import AstrologyChart
from bot.astrology.exception import AstrologyInvalidInput


class AstrologyCog(commands.Cog):
    """
    Comandos relacionados à astrologia
    """

    def __init__(self, client):
        self.client = client
        self.astrology_bot = AstrologyChart()

    @commands.command()
    async def mapa_astral(self, ctx, date=None, time=None, *args):
        """
        Visualize ou crie via DM seu mapa astral
        """
        city_name = ' '.join(args)
        if not isinstance(ctx.channel, discord.channel.DMChannel):
            user_chart = await self.astrology_bot.get_user_chart(ctx.author.id)
            if not user_chart:
                return await ctx.send('Você ainda não criou seu mapa astral. Para fazê-lo, mande esse comando via DM 😁')
            return await self.send_astrology_triad(ctx, user_chart)
        try:
            await ctx.trigger_typing()
            chart = await self.astrology_bot.calc_chart(ctx.author.id, date, time, city_name)
            await self.astrology_bot.save_chart(ctx.author.id, chart)
        except AstrologyInvalidInput as e:
            return await ctx.send(e.message)
        except Exception as e:
            logging.warning(e, exc_info=True)
            return await ctx.send(
                'Houve um erro momentâneo. Tente novamente em alguns segundos. Se o erro persistir, então pode ser algum bug. 😬')
        await self.send_astrology_triad(ctx, chart)

    async def send_astrology_triad(self, ctx, chart):
        sign = self.astrology_bot.get_sun_sign(chart)
        asc = self.astrology_bot.get_asc_sign(chart)
        moon = self.astrology_bot.get_moon_sign(chart)

        embed = discord.Embed(
            title='Seu mapa astral',
            description='Esse é sua tríade',
            colour=discord.Color.blurple(),
            timestamp=ctx.message.created_at
        )
        embed.add_field(name='Signo solar', value=sign)
        embed.add_field(name='Signo ascendente', value=asc)
        embed.add_field(name='Signo lunar', value=moon)
        await ctx.send(embed=embed)
