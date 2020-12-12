import logging

import discord

from bot import client, leaderboard_bot

@client.command(aliases=['lb'])
async def leaderboard(ctx, page=1):
    """
    Exibe o leaderboard de medalhas da Star Wars Wiki
    """
    await ctx.trigger_typing()
    try:
        leaderboard_data = await leaderboard_bot.get()
        leaderboard_result = leaderboard_bot.build_leaderboard(*leaderboard_data)
        leaderboard_img = await leaderboard_bot.draw_leaderboard(leaderboard_result, page)

        await ctx.send(file=discord.File(leaderboard_img, 'leaderboard.png'))
    except Exception as e:
        logging.warning(e, exc_info=True)
        return await ctx.send("Houve um erro ao obter o quadro de lideranças da Star Wars Wiki.")

@client.command(aliases=['medalha'])
async def medal(ctx, *args):
    """
    Exibe detalhes de uma medalha da Star Wars Wiki
    """
    medal_name = ' '.join(args)
    await ctx.trigger_typing()
    try:
        leaderboard_data = await leaderboard_bot.get()
        medals = await leaderboard_bot.build_medals_info(*leaderboard_data)
        
        medal_info = [medal for medal in medals if medal['name'] == medal_name]
        if not medal_info:
            return await ctx.send("Medalha não encontrada")
        
        medal_info = medal_info[0]
        embed = discord.Embed(
            title='Medalhas da Star Wars Wiki',
            description=medal_info['name'],
            colour=discord.Color.blurple(),
            timestamp=ctx.message.created_at
        )
        embed.set_thumbnail(url=medal_info['image_url'])
        embed.add_field(name='Descrição', value=medal_info['text'])
        embed.add_field(name='Pontos', value=medal_info['points'])
        await ctx.send(embed=embed)
    except Exception as e:
        logging.warning(e, exc_info=True)
        return await ctx.send("Houve um erro ao obter o quadro de lideranças da Star Wars Wiki.")

@client.command(aliases=['medalhas'])
async def medals(ctx, page: int=1):
    """
    Exibe as medalhas disponíveis da Star Wars Wiki
    """
    max_medals_per_page = 6
    await ctx.trigger_typing()
    if page < 0:
        page = 0
    try:
        leaderboard_data = await leaderboard_bot.get()
        medals = await leaderboard_bot.build_medals_info(*leaderboard_data)
        interval_start = (page-1) * max_medals_per_page
        interval_end = page * max_medals_per_page
        last_page = len(medals) // max_medals_per_page + (len(medals) % max_medals_per_page > 0)
        if page > last_page:
            return await ctx.send("Sem mais medalhas")
        
        embed = discord.Embed(
            title='Medalhas da Star Wars Wiki',
            description=f'Página {page}/{last_page}',
            colour=discord.Color.blurple(),
            timestamp=ctx.message.created_at
        )
        for medal_info in medals[interval_start:interval_end]:
            embed.add_field(name=medal_info['name'], value=medal_info['text'])
        return await ctx.send(embed=embed)
    except Exception as e:
        logging.warning(e, exc_info=True)
        return await ctx.send("Houve um erro ao obter o quadro de lideranças da Star Wars Wiki.")
