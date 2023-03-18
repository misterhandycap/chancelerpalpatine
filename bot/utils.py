import logging
import subprocess
from typing import Awaitable, Callable, Optional

import discord
from asyncio import get_running_loop, new_event_loop
from concurrent.futures.thread import ThreadPoolExecutor
from discord.ui import button, View
from functools import partial

from bot.chess.player import Player
from bot.i18n import i18n
from bot.servers import cache

server_configs = {}

try:
    current_bot_version = subprocess.check_output(["git", "describe", "--always"]).strip().decode()
except:
    current_bot_version = None

def i(interaction: discord.Interaction, text: str) -> str:
    if interaction.guild:
        server_id = interaction.guild.id
        lang = get_server_lang(server_id)
    else:
        lang = get_lang_from_user(interaction.user.id)
    return i18n(text, lang)

def get_server_lang(server_id):
    server_config = cache.get_config(server_id)
    if not server_config:
        return 'en'
    return server_config.language

def get_lang_from_user(user_id):
    server_user_is_in = [guild for guild in cache.all_servers if guild.get_member(user_id)]
    if not server_user_is_in:
        return 'en'
    server_langs = [get_server_lang(server.id) for server in server_user_is_in]
    return max(set(server_langs), key=server_langs.count)

def dm_only(interaction: discord.Interaction):
    return interaction.guild is None

def run_cpu_bound_task(func, *args, **kwargs):
    async def function_wrapper(*args, **kwargs):
        loop = get_running_loop()
        with ThreadPoolExecutor() as pool:
            return await loop.run_in_executor(pool, partial(func, *args, **kwargs))
    return function_wrapper

def run_cpu_bound_task_with_event_loop(func, *args, **kwargs):
    def function_wrapper(*args, **kwargs):
        event_loop = new_event_loop()
        try:
            corofn = func(*args, **kwargs)
            return event_loop.run_until_complete(corofn)
        finally:
            event_loop.close()
    return function_wrapper

def convert_users_to_players(*args):
        return tuple(map(lambda user: Player(user) if user else None, args))
    
server_language_to_tz = {
    'pt': 'America/Sao_Paulo',
    'en': 'UTC'
}


class PersonalView(View):
    def __init__(self, *, owner=discord.User, timeout: Optional[float]=180):
        self.owner = owner
        super().__init__(timeout=timeout)
    
    async def interaction_check(self, interaction: discord.Interaction):
        check = self._permission_check(interaction)
        if not check:
            await interaction.response.send_message(self._permission_denied_message(interaction),
                ephemeral=True, delete_after=3)
        return check
        
    def _permission_check(self, interaction: discord.Interaction):
        return interaction.user == self.owner
    
    def _permission_denied_message(self, interaction: discord.Interaction):
        return i(interaction, "Only user {username} may react to this message").format(username=self.owner.name)


def paginate(elems: list, page: int, itens_per_page: int):
    """
    Paginates long list into pages and returns requested page

    Pages indexes start at 1.

    :param elems: Elements to be paginated
    :type elems: list
    :param page: Page number to be returned
    :type page: int
    :param itens_per_page: Max number of elements per page
    :type itens_per_page: int
    :return: Paginated list
    :rtype: list
    """
    len_elems = len(elems)
    last_page = len_elems // itens_per_page + (len_elems % itens_per_page > 0)
    page = min(max(page, 1), last_page)
    interval_start = (page-1) * itens_per_page
    interval_end = page * itens_per_page
    return elems[interval_start:interval_end], last_page


class PaginatedEmbedManager():
    """
    Utility for managing paginated embed via Discord UI Buttons

    :param embed_func: Function responsible for creating paginated embed
    :type embed_func: function
    """
    
    BACKWARD_EMOJI = '◀️'
    FORWARD_EMOJI = '▶️'

    def __init__(self, embed_func: Callable[[int, discord.Message], Awaitable[discord.Embed]]):
        self.last_page = None
        self.embed_title: str = None
        self.callback = embed_func
        self.interaction: discord.Interaction = None

    async def send_embed(self, embed: discord.Embed, page_number: int,
                         interaction: discord.Interaction, discord_file: discord.File=None,
                         content=None):
        """
        Prepares and sends given paginated embed. Also reacts with navigation emojis

        :param embed: Paginated embed
        :type embed: discord.Embed
        :param page_number: Page number
        :type page_number: int
        :param interaction: Discordpy's interaction
        :type interaction: discord.Interaction
        :return: Sent message
        :rtype: discord.Message
        """
        self.embed_title = embed.title
        self.interaction = interaction
        pagination_view = PaginationView(
            owner=interaction.user, page=page_number, last_page=self.last_page,
            embed_send_func=lambda x: self._send_updated_embed(x))
        embed = self._prepare_embed(embed, interaction.user, page_number)
        if interaction.response.is_done():
            await self.interaction.edit_original_response(
                embed=embed, content=content, view=pagination_view)
        else:
            await interaction.response.send_message(
                embed=embed, file=discord_file, content=content, view=pagination_view)
        return await interaction.original_response()

    def _prepare_embed(self, embed, author_name, page_number):
        embed.set_author(name=author_name)
        embed.set_footer(text=f'{page_number}/{self.last_page}')
        return embed
    
    async def _send_updated_embed(self, page: int):
        message = await self.interaction.original_response()
        
        try:
            embed = self._prepare_embed(
                await self.callback(page, message), self.interaction.user, page)
            await self.interaction.edit_original_response(embed=embed)
        except Exception as e:
            logging.warning(f'{e.__class__}: {e}')
            await self.interaction.edit_original_response(content='⚠️')


class PaginationView(PersonalView):
    def __init__(self, *, owner: discord.User, page: int=0, last_page: int=None,
                 embed_send_func: Callable[[int], Awaitable], timeout: Optional[float]=180):
        self.value: int = page
        self.last_page = last_page
        self.callback = embed_send_func
        super().__init__(owner=owner, timeout=timeout)
        
    @button(emoji='◀️')
    async def previous_page(self, interaction: discord.Interaction, _):
        await interaction.response.defer(thinking=False)
        self.value = max(self.value - 1, 1)
        await self.callback(self.value)
    
    @button(emoji='▶️')
    async def next_page(self, interaction: discord.Interaction, _):
        await interaction.response.defer(thinking=False)
        self.value = min(self.value + 1, self.last_page)
        await self.callback(self.value)
