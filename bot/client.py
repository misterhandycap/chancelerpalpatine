import discord
from discord.ext import commands
from dotenv import load_dotenv

from bot.chess import Chess

load_dotenv()

client = discord.Client()

client = commands.Bot(command_prefix = 'cp!')

chess_bot = Chess()
chess_bot.load_games()
