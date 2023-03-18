import logging

import discord
from discord import app_commands

from bot.sww_leaderboard.leaderboard import Leaderboard
from bot.utils import i, paginate, PaginatedEmbedManager


class StarWarsWikiCmds(app_commands.Group):
    """
    Comandos da Star Wars Wiki em Português
    """

    def __init__(self, client):
        self.client = client
        self.leaderboard_bot = Leaderboard()
        self.medals_paginated_embed_manager = PaginatedEmbedManager(self._build_medals_embed)
        super().__init__(name='sww')

    @app_commands.command(
        name="leaderboard",
        description="Exibe o leaderboard de medalhas da Star Wars Wiki"
    )
    @app_commands.describe(page='Página')
    async def leaderboard(self, interaction: discord.Interaction, page: int=1):
        """
        Exibe o leaderboard de medalhas da Star Wars Wiki
        """
        await interaction.response.defer()
        try:
            leaderboard_data = await self.leaderboard_bot.get()
            leaderboard_result = self.leaderboard_bot.build_leaderboard(*leaderboard_data)
            leaderboard_img = await self.leaderboard_bot.draw_leaderboard(leaderboard_result, page)

            await interaction.followup.send(file=discord.File(leaderboard_img, 'leaderboard.png'))
        except Exception as e:
            logging.warning(e, exc_info=True)
            return await interaction.followup.send(i(interaction, "Something went wrong when trying to fetch Star Wars Wiki's leaderboard"))

    @app_commands.command(
        name="medal",
        description="Exibe detalhes de uma medalha da Star Wars Wiki",
    )
    @app_commands.describe(medal_name='Nome da medalha')
    async def medal(self, interaction: discord.Interaction, medal_name: str):
        """
        Exibe detalhes de uma medalha da Star Wars Wiki
        """
        await interaction.response.defer()
        try:
            leaderboard_data = await self.leaderboard_bot.get()
            medals = await self.leaderboard_bot.build_medals_info(*leaderboard_data)
            
            medal_info = [medal for medal in medals if medal['name'] == medal_name]
            if not medal_info:
                return await interaction.followup.send(i(interaction, "Medal not found"))
            
            medal_info = medal_info[0]
            embed = discord.Embed(
                title=i(interaction, "Star Wars Wiki's medals"),
                description=medal_info['name'],
                colour=discord.Color.blurple()
            )
            embed.set_thumbnail(url=medal_info['image_url'])
            embed.add_field(name=i(interaction, 'Description'), value=medal_info['text'])
            embed.add_field(name=i(interaction, 'Points'), value=medal_info['points'])
            await interaction.followup.send(embed=embed)
        except Exception as e:
            logging.warning(e, exc_info=True)
            return await interaction.followup.send(i(interaction, "Something went wrong when trying to fetch Star Wars Wiki's leaderboard"))

    @app_commands.command(
        name="medals",
        description="Exibe as medalhas disponíveis da Star Wars Wiki",
    )
    @app_commands.describe(page='Página')
    async def medals(self, interaction: discord.Interaction, page: int=1):
        """
        Exibe as medalhas disponíveis da Star Wars Wiki
        """
        await interaction.response.defer()
        try:
            return await self.medals_paginated_embed_manager.send_embed(
                await self._build_medals_embed(page, interaction), page, interaction)
        except Exception as e:
            logging.warning(e, exc_info=True)
            return await interaction.followup.send(i(interaction, "Something went wrong when trying to fetch Star Wars Wiki's leaderboard"))

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
