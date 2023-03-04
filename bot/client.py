import logging
import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

from bot.across_the_stars_cmds import AcrossTheStarsCmds
from bot.akinator_cmds import AkinatorCmds
from bot.anime_cmds import AnimeCmds
from bot.chess_cmds import ChessCmds
from bot.general_cmds import GeneralCmds
from bot.level_cmds import LevelCmds
from bot.palplatina_cmds import PalplatinaCmds
from bot.sww_cmds import StarWarsWikiCmds

load_dotenv()

discord.utils.setup_logging(level=logging.DEBUG if os.environ.get("DEBUG") else logging.INFO)

intents = discord.Intents.default()
intents.members = True
intents.presences = True
intents.message_content = True


class BotClient(commands.Bot):
    
    async def setup_hook(self) -> None:
        testing_guild_id = int(os.environ.get("TESTING_GUILD_ID", 0))
        if testing_guild_id:
            guild = discord.Object(id=testing_guild_id)
            self.tree.copy_global_to(guild=guild)
            logging.info(f'Syncing commands to guild {testing_guild_id}')
        else:
            guild = None
        await self.tree.sync(guild=guild)
        logging.info(f'Synced tree... {[x.name for x in self.tree.get_commands()]}')
        return await super().setup_hook()


client = BotClient(
    command_prefix=os.environ.get("BOT_PREFIX", 'cp!'),
    intents=intents
)

client.tree.add_command(GeneralCmds(client))
client.tree.add_command(LevelCmds(client))
client.tree.add_command(ChessCmds(client))
client.tree.add_command(AkinatorCmds(client))
client.tree.add_command(AnimeCmds(client))
client.tree.add_command(StarWarsWikiCmds(client))
client.tree.add_command(AcrossTheStarsCmds(client))
client.tree.add_command(PalplatinaCmds(client))

astrology_bot = None
if os.environ.get("DISABLE_ASTROLOGY") not in ['True', 'true']:
    from bot.astrology_cmds import AstrologyCmds
    client.tree.add_command(AstrologyCmds(client))
