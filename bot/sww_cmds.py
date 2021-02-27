import logging

import discord
from discord.ext import commands

from bot.i18n import _
from bot.sww_leaderboard.leaderboard import Leaderboard
from bot.utils import paginate, PaginatedEmbedManager


class StarWarsWikiCog(commands.Cog):
    """
    Comandos da Star Wars Wiki em Português
    """

    def __init__(self, client):
        self.client = client
        self.leaderboard_bot = Leaderboard()
        self.medals_paginated_embed_manager = PaginatedEmbedManager(
            client, self._build_medals_embed)

    @commands.command(aliases=['lb'])
    async def leaderboard(self, ctx, page: int=1):
        """
        Exibe o leaderboard de medalhas da Star Wars Wiki
        """
        await ctx.trigger_typing()
        try:
            leaderboard_data = await self.leaderboard_bot.get()
            leaderboard_result = self.leaderboard_bot.build_leaderboard(*leaderboard_data)
            leaderboard_img = await self.leaderboard_bot.draw_leaderboard(leaderboard_result, page)

            await ctx.send(file=discord.File(leaderboard_img, 'leaderboard.png'))
        except Exception as e:
            logging.warning(e, exc_info=True)
            return await ctx.send(_("Something went wrong when trying to fetch Star Wars Wiki's leaderboard"))

    @commands.command(aliases=['medalha'])
    async def medal(self, ctx, *, medal_name):
        """
        Exibe detalhes de uma medalha da Star Wars Wiki
        """
        await ctx.trigger_typing()
        try:
            leaderboard_data = await self.leaderboard_bot.get()
            medals = await self.leaderboard_bot.build_medals_info(*leaderboard_data)
            
            medal_info = [medal for medal in medals if medal['name'] == medal_name]
            if not medal_info:
                return await ctx.send(_("Medal not found"))
            
            medal_info = medal_info[0]
            embed = discord.Embed(
                title=_("Star Wars Wiki's medals"),
                description=medal_info['name'],
                colour=discord.Color.blurple(),
                timestamp=ctx.message.created_at
            )
            embed.set_thumbnail(url=medal_info['image_url'])
            embed.add_field(name=_('Description'), value=medal_info['text'])
            embed.add_field(name=_('Points'), value=medal_info['points'])
            await ctx.send(embed=embed)
        except Exception as e:
            logging.warning(e, exc_info=True)
            return await ctx.send(_("Something went wrong when trying to fetch Star Wars Wiki's leaderboard"))

    @commands.command(aliases=['medalhas'])
    async def medals(self, ctx, page: int=1):
        """
        Exibe as medalhas disponíveis da Star Wars Wiki
        """
        await ctx.trigger_typing()
        try:
            return await self.medals_paginated_embed_manager.send_embed(
                await self._build_medals_embed(page), page, ctx)
        except Exception as e:
            logging.warning(e, exc_info=True)
            return await ctx.send(_("Something went wrong when trying to fetch Star Wars Wiki's leaderboard"))

    async def _build_medals_embed(self, page_number):
        max_medals_per_page = 6
        leaderboard_data = await self.leaderboard_bot.get()
        medals = await self.leaderboard_bot.build_medals_info(*leaderboard_data)
        paginated_medals, last_page = paginate(medals, page_number, max_medals_per_page)
        
        embed = discord.Embed(
            title=_("Star Wars Wiki's medals"),
            description=f'{_("Page")} {max(page_number, 1)}/{last_page}',
            colour=discord.Color.blurple()
        )
        for medal_info in paginated_medals:
            embed.add_field(name=medal_info['name'], value=medal_info['text'])
        self.medals_paginated_embed_manager.last_page = last_page

        return embed
