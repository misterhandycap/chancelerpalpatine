import logging

import discord
from discord.ext import commands
from discord_slash import cog_ext
from discord_slash.utils.manage_commands import create_option

from bot.sww_leaderboard.leaderboard import Leaderboard
from bot.utils import i, paginate, PaginatedEmbedManager


class StarWarsWikiCog(commands.Cog):
    """
    Comandos da Star Wars Wiki em Português
    """

    def __init__(self, client):
        self.client = client
        self.leaderboard_bot = Leaderboard()
        self.medals_paginated_embed_manager = PaginatedEmbedManager(
            client, self._build_medals_embed)

    @cog_ext.cog_slash(
        name="leaderboard",
        description="Exibe o leaderboard de medalhas da Star Wars Wiki",
        options=[
            create_option(name="page", description="Página", option_type=4, required=False),
        ],
        guild_ids=[297129074692980737]
    )
    async def leaderboard(self, ctx, page: int=1):
        """
        Exibe o leaderboard de medalhas da Star Wars Wiki
        """
        await ctx.defer()
        try:
            leaderboard_data = await self.leaderboard_bot.get()
            leaderboard_result = self.leaderboard_bot.build_leaderboard(*leaderboard_data)
            leaderboard_img = await self.leaderboard_bot.draw_leaderboard(leaderboard_result, page)

            await ctx.send(file=discord.File(leaderboard_img, 'leaderboard.png'))
        except Exception as e:
            logging.warning(e, exc_info=True)
            return await ctx.send(i(ctx, "Something went wrong when trying to fetch Star Wars Wiki's leaderboard"))

    @cog_ext.cog_slash(
        name="medal",
        description="Exibe detalhes de uma medalha da Star Wars Wiki",
        options=[
            create_option(name="medal_name", description="Nome da medalha", option_type=3, required=True)
        ],
        guild_ids=[297129074692980737]
    )
    async def medal(self, ctx, medal_name):
        """
        Exibe detalhes de uma medalha da Star Wars Wiki
        """
        await ctx.defer()
        try:
            leaderboard_data = await self.leaderboard_bot.get()
            medals = await self.leaderboard_bot.build_medals_info(*leaderboard_data)
            
            medal_info = [medal for medal in medals if medal['name'] == medal_name]
            if not medal_info:
                return await ctx.send(i(ctx, "Medal not found"))
            
            medal_info = medal_info[0]
            embed = discord.Embed(
                title=i(ctx, "Star Wars Wiki's medals"),
                description=medal_info['name'],
                colour=discord.Color.blurple()
            )
            embed.set_thumbnail(url=medal_info['image_url'])
            embed.add_field(name=i(ctx, 'Description'), value=medal_info['text'])
            embed.add_field(name=i(ctx, 'Points'), value=medal_info['points'])
            await ctx.send(embed=embed)
        except Exception as e:
            logging.warning(e, exc_info=True)
            return await ctx.send(i(ctx, "Something went wrong when trying to fetch Star Wars Wiki's leaderboard"))

    @cog_ext.cog_slash(
        name="medals",
        description="Exibe as medalhas disponíveis da Star Wars Wiki",
        options=[
            create_option(name="page", description="Página", option_type=4, required=False),
        ],
        guild_ids=[297129074692980737]
    )
    async def medals(self, ctx, page: int=1):
        """
        Exibe as medalhas disponíveis da Star Wars Wiki
        """
        await ctx.defer()
        try:
            return await self.medals_paginated_embed_manager.send_embed(
                await self._build_medals_embed(page, ctx), page, ctx)
        except Exception as e:
            logging.warning(e, exc_info=True)
            return await ctx.send(i(ctx, "Something went wrong when trying to fetch Star Wars Wiki's leaderboard"))

    async def _build_medals_embed(self, page_number, original_message):
        max_medals_per_page = 6
        leaderboard_data = await self.leaderboard_bot.get()
        medals = await self.leaderboard_bot.build_medals_info(*leaderboard_data)
        paginated_medals, last_page = paginate(medals, page_number, max_medals_per_page)
        
        embed = discord.Embed(
            title=i(original_message, "Star Wars Wiki's medals"),
            description=f'{i(original_message, "Page")} {max(page_number, 1)}/{last_page}',
            colour=discord.Color.blurple()
        )
        for medal_info in paginated_medals:
            embed.add_field(name=medal_info['name'], value=medal_info['text'])
        self.medals_paginated_embed_manager.last_page = last_page

        return embed
