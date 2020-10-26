import discord

from bot import client
from bot.sww_leaderboard.leaderboard import Leaderboard

@client.command(aliases=['lb'])
async def leaderboard(ctx):
    await ctx.trigger_typing()
    leaderboard_bot = Leaderboard()

    try:
        leaderboard_data = await leaderboard_bot.get()
        leaderboard_result = leaderboard_bot.build_leaderboard(*leaderboard_data)
        leaderboard_img = await leaderboard_bot.draw_leaderboard(leaderboard_result)

        await ctx.send(file=discord.File(leaderboard_img, 'leaderboard.png'))
    except Exception as e:
        print(e)
        return await ctx.send("Houve um erro ao obter o quadro de lideranças da Star Wars Wiki.")
