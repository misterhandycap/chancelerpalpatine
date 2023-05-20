import logging
import os
from typing import Any, Callable, List

import discord
import discordhealthcheck
from discord.ext import commands
from dotenv import load_dotenv

from bot.across_the_stars_cmds import AcrossTheStarsCmds
from bot.akinator_cmds import AkinatorCmds
from bot.anime_cmds import AnimeCmds
from bot.chess_cmds import ChessCmds
from bot.general_cmds import GeneralCmds
from bot.level_cmds import LevelCmds
from bot.misc.scheduler import Scheduler
from bot.palplatina_cmds import PalplatinaCmds
from bot.servers import cache
from bot.sww_cmds import StarWarsWikiCmds

load_dotenv()

discord.utils.setup_logging(level=logging.DEBUG if os.environ.get("DEBUG") else logging.INFO)

intents = discord.Intents.default()
intents.members = True
intents.presences = True
intents.message_content = True


class BotClient(commands.Bot):
    
    scheduler_bot: Scheduler
    scheduler_callbacks: List[Callable[[Scheduler], Any]] = []
    
    async def setup_hook(self) -> None:
        testing_guild_id = int(os.environ.get("TESTING_GUILD_ID", 0) or 0)
        if testing_guild_id:
            guild = discord.Object(id=testing_guild_id)
            self.tree.copy_global_to(guild=guild)
            logging.info(f'Syncing commands to guild {testing_guild_id}')
        else:
            guild = None
        await self.tree.sync(guild=guild)
        logging.info(f'Synced tree... {[x.name for x in self.tree.get_commands()]}')
        self.healthcheck_server = await discordhealthcheck.start(self)
        return await super().setup_hook()
    
    async def on_ready(self):
        await self.change_presence(
            status=discord.Status.online,
            activity=discord.Game(f'Planejando uma ordem surpresa')
        )
        await cache.load_configs()
        cache.all_servers = self.guilds
        self.scheduler_bot = Scheduler(event_loop=self.loop)
        self.scheduler_bot.start()
        for callback in self.scheduler_callbacks:
            callback(self.scheduler_bot)
        logging.info('Bot is ready')
        
    async def on_interaction(self, interaction: discord.Interaction):
        if interaction.command:
            interaction_name = interaction.command.qualified_name
        elif interaction.message.interaction:
            interaction_name = f"Component from {interaction.message.interaction.name}"
        else:
            interaction_name = "Component"
        user_id = interaction.user.id
        guild_id = interaction.guild_id or 'DM'
        logging.info(f'{interaction_name} interaction by user {user_id} requested on {guild_id}')
        
    async def on_app_command_completion(self, interaction: discord.Interaction, _):
        guild_id = interaction.guild_id or 'DM'
        logging.info(f'{interaction.command.qualified_name} interaction by user {interaction.user.id} completed on {guild_id}')


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
