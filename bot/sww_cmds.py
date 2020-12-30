import logging

import discord
from discord.ext import commands

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
    async def leaderboard(self, ctx, page=1):
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
            return await ctx.send("Houve um erro ao obter o quadro de lideranças da Star Wars Wiki.")

    @commands.command(aliases=['medalha'])
    async def medal(self, ctx, *args):
        """
        Exibe detalhes de uma medalha da Star Wars Wiki
        """
        medal_name = ' '.join(args)
        await ctx.trigger_typing()
        try:
            leaderboard_data = await self.leaderboard_bot.get()
            medals = await self.leaderboard_bot.build_medals_info(*leaderboard_data)
            
            medal_info = [medal for medal in medals if medal['name'] == medal_name]
            if not medal_info:
                return await ctx.send("Medalha não encontrada")
            
            medal_info = medal_info[0]
            embed = discord.Embed(
                title='Medalhas da Star Wars Wiki',
                description=medal_info['name'],
                colour=discord.Color.blurple(),
                timestamp=ctx.message.created_at
            )
            embed.set_thumbnail(url=medal_info['image_url'])
            embed.add_field(name='Descrição', value=medal_info['text'])
            embed.add_field(name='Pontos', value=medal_info['points'])
            await ctx.send(embed=embed)
        except Exception as e:
            logging.warning(e, exc_info=True)
            return await ctx.send("Houve um erro ao obter o quadro de lideranças da Star Wars Wiki.")

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
            return await ctx.send("Houve um erro ao obter o quadro de lideranças da Star Wars Wiki.")

    async def _build_medals_embed(self, page_number):
        max_medals_per_page = 6
        leaderboard_data = await self.leaderboard_bot.get()
        medals = await self.leaderboard_bot.build_medals_info(*leaderboard_data)
        paginated_medals, last_page = paginate(medals, page_number, max_medals_per_page)
        
        embed = discord.Embed(
            title='Medalhas da Star Wars Wiki',
            description=f'Página {max(page_number, 1)}/{last_page}',
            colour=discord.Color.blurple()
        )
        for medal_info in paginated_medals:
            embed.add_field(name=medal_info['name'], value=medal_info['text'])
        self.medals_paginated_embed_manager.last_page = last_page

        return embed