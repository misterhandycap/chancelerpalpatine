import logging

import discord

from bot import astrology_bot, client
from bot.astrology.exception import AstrologyInvalidInput

@client.command()
async def mapa_astral(ctx, date=None, time=None, *args):
    city_name = ' '.join(args)
    if not isinstance(ctx.channel, discord.channel.DMChannel):
        user_chart = astrology_bot.get_user_chart(ctx.author.id)
        if not user_chart:
            return await ctx.send('Você ainda não criou seu mapa astral. Para fazê-lo, mande esse comando via DM 😁')
        return await send_astrology_triad(ctx, user_chart.chart)
    try:
        await ctx.trigger_typing()
        chart = await astrology_bot.calc_chart(ctx.author.id, date, time, city_name)
    except AstrologyInvalidInput as e:
        return await ctx.send(e.message)
    except Exception as e:
        logging.warning(e, exc_info=True)
        return await ctx.send(
            'Houve um erro momentâneo. Tente novamente em alguns segundos. Se o erro persistir, então pode ser algum bug. 😬')
    await send_astrology_triad(ctx, chart)

async def send_astrology_triad(ctx, chart):
    sign = astrology_bot.get_sun_sign(chart)
    asc = astrology_bot.get_asc_sign(chart)
    moon = astrology_bot.get_moon_sign(chart)

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
