import discord
from discord.ext import commands

bot = commands.Bot(command_prefix = '.')

@bot.event
async def on_ready():
    print('Its time to reveal ourselves.')

bot.run('NzUxMDg3NjY1OTUyMDYzNTgw.X1D-5g.omB-ZX0U8YIyzFd3sWi-rRaBjvs')
