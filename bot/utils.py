import os
import re

from asyncio import get_running_loop, new_event_loop
from concurrent.futures.thread import ThreadPoolExecutor
from functools import partial

from bot.chess.player import Player

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
    Utility for managing paginated embed via user reactions

    :param client: Discord bot client
    :type client: discord.Bot
    :param embed_func: Function responsible for creating paginated embed
    :type embed_func: function
    """
    
    BACKWARD_EMOJI = '◀️'
    FORWARD_EMOJI = '▶️'

    def __init__(self, client, embed_func):
        self.last_page = None
        self.embed_title = None
        self.callback = embed_func
        client.add_listener(self._on_reaction_add, 'on_reaction_add')

    async def send_embed(self, embed, page_number, ctx):
        """
        Prepares and sends given paginated embed. Also reacts with navigation emojis

        :param embed: Paginated embed
        :type embed: discord.Embed
        :param page_number: Page number
        :type page_number: int
        :param ctx: Discordpy's context
        :type ctx: discord.ext.commands.Context
        :return: Sent message
        :rtype: discord.Message
        """
        self.embed_title = embed.title
        embed = self._prepare_embed(embed, ctx.author, page_number)
        message = await ctx.send(embed=embed)
        await message.add_reaction(self.BACKWARD_EMOJI)
        await message.add_reaction(self.FORWARD_EMOJI)
        return message

    def _prepare_embed(self, embed, author_name, page_number):
        embed.set_author(name=author_name)
        embed.set_footer(text=f'{page_number}/{self.last_page}')
        return embed

    async def _on_reaction_add(self, reaction, user):
        valid_emojis = [self.BACKWARD_EMOJI, self.FORWARD_EMOJI]
        if not reaction.message.embeds:
            return
        embed = reaction.message.embeds[0]
        if not (embed.title == self.embed_title and str(user) == embed.author.name):
            return

        emoji = str(reaction)
        if emoji not in valid_emojis:
            return

        match = re.match(r'(\d+)\/(\d+)', embed.footer.text)
        if not match:
            page_number = 1
            last_page = 1
        else:
            page_number = int(match.group(1))
            last_page = int(match.group(2))
        
        if emoji == self.BACKWARD_EMOJI and page_number > 1:
            page_number -= 1
        elif emoji == self.FORWARD_EMOJI and page_number < last_page:
            page_number += 1

        try:
            embed = self._prepare_embed(
                await self.callback(page_number), str(user), page_number)
            await reaction.message.edit(embed=embed)
        except:
            return await reaction.message.add_reaction('⚠️')
        await reaction.message.remove_reaction(emoji, user)
