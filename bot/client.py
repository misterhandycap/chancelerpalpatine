import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

from bot.akinator.akinator_game import AkinatorGame
from bot.astrology.astrology_chart import AstrologyChart
from bot.chess.chess import Chess
from bot.chess.puzzle import Puzzle
from bot.sww_leaderboard.leaderboard import Leaderboard

load_dotenv()

client = discord.Client()

client = commands.Bot(command_prefix=os.environ.get("BOT_PREFIX", 'cp!'))

chess_bot = Chess()
chess_bot.load_games()

astrology_bot = AstrologyChart()
astrology_bot.load_charts()

puzzle_bot = Puzzle()

akinator_bot = AkinatorGame()

leaderboard_bot = Leaderboard()
