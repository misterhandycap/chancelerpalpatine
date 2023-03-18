import logging
from typing import Awaitable, Callable, Optional

import discord
from discord.ui import button, View

from bot.i18n import i18n
from bot.servers import cache

server_language_to_tz = {
    'pt': 'America/Sao_Paulo',
    'en': 'UTC'
}

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
