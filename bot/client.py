import discord
from discord.ext import commands

from bot.chess import Chess

client = discord.Client()

client = commands.Bot(command_prefix = 'cp!')

chess_bot = Chess()
chess_bot.load_games()
