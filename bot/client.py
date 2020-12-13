import logging
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

from bot.akinator_cmds import AkinatorCog
from bot.anime_cmds import AnimeCog
from bot.chess_cmds import ChessCog
from bot.level import LevelCog
from bot.sww_cmds import StarWarsWikiCog

load_dotenv()

logging.basicConfig(level=logging.DEBUG if os.environ.get("DEBUG") else logging.WARNING)

client = discord.Client()

client = commands.Bot(command_prefix=os.environ.get("BOT_PREFIX", 'cp!'))

client.add_cog(LevelCog(client))
client.add_cog(ChessCog(client))
client.add_cog(AkinatorCog(client))
client.add_cog(AnimeCog(client))
client.add_cog(StarWarsWikiCog(client))

astrology_bot = None
if os.environ.get("DISABLE_ASTROLOGY") not in ['True', 'true']:
    from bot.astrology_cmds import AstrologyCog
    client.add_cog(AstrologyCog(client))
