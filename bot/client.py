import logging
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

from bot.across_the_stars_cmds import AcrossTheStarsCmds
from bot.akinator_cmds import AkinatorCog
from bot.anime_cmds import AnimeCog
from bot.chess_cmds import ChessCog
from bot.general import GeneralCog
from bot.level import LevelCog
from bot.music_cmds import MusicCog
from bot.palplatina_cmds import PalplatinaCmds
from bot.sww_cmds import StarWarsWikiCog

load_dotenv()

logging.basicConfig(level=logging.DEBUG if os.environ.get("DEBUG") else logging.INFO)

intents = discord.Intents.default()
intents.members = True
intents.presences = True

client = commands.Bot(
    command_prefix=os.environ.get("BOT_PREFIX", 'cp!'),
    help_command=None,
    intents=intents
)

client.add_cog(GeneralCog(client))
client.add_cog(LevelCog(client))
client.add_cog(ChessCog(client))
client.add_cog(AkinatorCog(client))
client.add_cog(AnimeCog(client))
client.add_cog(StarWarsWikiCog(client))
client.add_cog(PalplatinaCmds(client))
client.add_cog(AcrossTheStarsCmds(client))
client.add_cog(MusicCog(client))

astrology_bot = None
if os.environ.get("DISABLE_ASTROLOGY") not in ['True', 'true']:
    from bot.astrology_cmds import AstrologyCog
    client.add_cog(AstrologyCog(client))
