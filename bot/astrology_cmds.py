import discord

from bot import client
from bot.astrology.astrology_chart import calc_chart, get_asc_sign, get_moon_sign, get_sun_sign

@client.command()
async def mapa_astral(ctx, date=None, time=None, city_name=None):
    if not isinstance(ctx.channel, discord.channel.DMChannel):
        return await ctx.send('Mande esse comando via DM 😁')
    try:
        chart = calc_chart(date, time, city_name)
    except:
        return await ctx.send('Formato inválido! Formato esperado: `cp!mapa astral YYYY/MM/DD HH:MM NomeCidade`')
    sign = get_sun_sign(chart)
    asc = get_asc_sign(chart)
    moon = get_moon_sign(chart)

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
