import logging

import discord

from bot import client, leaderboard_bot

@client.command(aliases=['lb'])
async def leaderboard(ctx, page=1):
    await ctx.trigger_typing()
    try:
        leaderboard_data = await leaderboard_bot.get()
        leaderboard_result = leaderboard_bot.build_leaderboard(*leaderboard_data)
        leaderboard_img = await leaderboard_bot.draw_leaderboard(leaderboard_result, page)

        await ctx.send(file=discord.File(leaderboard_img, 'leaderboard.png'))
    except Exception as e:
        logging.warning(e, exc_info=True)
        return await ctx.send("Houve um erro ao obter o quadro de lideranças da Star Wars Wiki.")

@client.command(aliases=['medalha', 'medalhas', 'medal'])
async def medals(ctx, medal_name=None):
    await ctx.trigger_typing()
    try:
        leaderboard_data = await leaderboard_bot.get()
        medals = await leaderboard_bot.build_medals_info(*leaderboard_data)
        if not medal_name:
            final_text = "Essas são as medalhas disponíveis na Star Wars Wiki:\n```"
            for medal_info in medals:
                final_text += f"* {medal_info['name']}\n"
            final_text += "```\n"
            return await ctx.send(final_text)
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