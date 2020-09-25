import discord

from bot import astrology_bot, client

@client.command()
async def mapa_astral(ctx, date=None, time=None, city_name=None):
    if not isinstance(ctx.channel, discord.channel.DMChannel):
        user_chart = astrology_bot.get_user_chart(ctx.author.id)
        if not user_chart:
            return await ctx.send('Você ainda não criou seu mapa astral. Para fazê-lo, mande esse comando via DM 😁')
        return await send_astrology_triad(ctx, user_chart.chart)
    try:
        chart = astrology_bot.calc_chart(ctx.author.id, date, time, city_name)
    except:
        return await ctx.send('Formato inválido! Formato esperado: `cp!mapa astral YYYY/MM/DD HH:MM NomeCidade`')
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
