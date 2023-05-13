import logging
from typing import Any, Coroutine, TYPE_CHECKING

import discord
from discord import app_commands, Embed, TextStyle
from discord.enums import TextStyle
from discord.interactions import Interaction
from discord.ui import TextInput, View, button, Modal
from pywikibot import showDiff

from bot.discord_helpers import i, PaginatedEmbedManager
from bot.misc.scheduler import Scheduler
from bot.sww.leaderboard import Leaderboard
from bot.sww.timeline_translator import TimelineTranslator
from bot.utils import paginate

if TYPE_CHECKING:
    from bot.client import BotClient


class StarWarsWikiCmds(app_commands.Group):
    """
    Comandos da Star Wars Wiki em Português
    """

    def __init__(self, client: 'BotClient'):
        self.client = client
        self.client.scheduler_callbacks.append(self._schedule_timeline)
        self.timeline_translator = TimelineTranslator()
        self.leaderboard_bot = Leaderboard()
        self.medals_paginated_embed_manager = PaginatedEmbedManager(self._build_medals_embed)
        super().__init__(name='sww')

    def _schedule_timeline(self, scheduler_bot: Scheduler):
        pass
    
    @app_commands.command(
        name="linha_do_tempo",
        description="Tradução da linha do tempo de mídia canônica"
    )
    async def translate_timeline(self, interaction: discord.Interaction):
        await interaction.response.defer(thinking=False)
        
        await self.timeline_translator.login()
        await self.timeline_translator.get_wookiee_page()
        await self.timeline_translator.get_timeline_page()
        for ref_name, ref_txt in self.timeline_translator.build_new_references().items():
            timeline_view = TimelineView()
            embed = Embed(
                title=i(interaction, "Timeline of canon media"),
                description=i(interaction,
                              "Contribute to Star Wars Wiki by translating the selected references to the timeline of canon media")
            )
            embed.add_field(name=i(interaction, 'Reference name'), value=ref_name, inline=False)
            embed.add_field(name=i(interaction, 'Reference content'), value=ref_txt, inline=False)
            message = await interaction.channel.send(embed=embed, view=timeline_view)
            await timeline_view.wait()
            translated_text = timeline_view.value or ref_txt
            self.timeline_translator.add_reference_translation(ref_name, translated_text)
            
            embed.add_field(name=i(interaction, 'Translation'), value=translated_text, inline=False)
            embed.set_author(name=interaction.user)
            await message.edit(embed=embed, view=None)
        self.timeline_translator.translate_page()
        
        try:
            await self.timeline_translator.save_page()
            
            if self.timeline_translator._current_content == self.timeline_translator.page.text:
                embed = Embed(
                    title=i(interaction, "Timeline of canon media"),
                    url=self.timeline_translator.page.full_url(),
                    description=i(interaction, "No new content to translate")
                )
            else:
                embed = Embed(
                    title=i(interaction, "Timeline of canon media"),
                    url=self.timeline_translator.get_diff_url(),
                    colour=discord.Color.green(),
                    description=i(interaction,
                                "Page has been successfully updated with new content. Please, check the persisted modifications to ensure that everything is correct.")
                )
            await interaction.channel.send(embed=embed)
        except Exception as e:
            embed = Embed(
                title=i(interaction, "Timeline of canon media"),
                colour=discord.Color.red(),
                description=i(interaction, "An error has occurred. Ask the admin to check for details.")
            )
            logging.exception(e)
            await interaction.channel.send(embed=embed)
    
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
    
    
class TimelineView(View):
    def __init__(self, *, timeout: float | None = None):
        super().__init__(timeout=timeout)
        self.value: str = None
        
    @button(label='Adicionar tradução', style=discord.ButtonStyle.green)
    async def open_modal(self, interaction: discord.Interaction, _):
        await interaction.response.send_modal(TimelineModal(self, title="Tradução de referência"))
        
    @button(label='Manter texto original', style=discord.ButtonStyle.secondary)
    async def dismiss(self, interaction: discord.Interaction, _):
        await interaction.response.defer(thinking=False)
        self.stop()
        

class TimelineModal(Modal):
    translation = TextInput(label='Tradução', style=TextStyle.long)
    
    def __init__(self, view: TimelineView, **kwargs) -> None:
        self.view = view
        super().__init__(**kwargs)
    
    async def on_submit(self, interaction: Interaction) -> Coroutine[Any, Any, None]:
        await interaction.response.defer(thinking=False)
        self.view.value = self.translation.value
        self.view.stop()
