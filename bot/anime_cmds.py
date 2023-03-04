import logging

import discord
from discord import app_commands

from bot.anime.anime import Anime
from bot.utils import i


class AnimeCmds(app_commands.Group):
    """
    Comandos de anime
    """

    def __init__(self, client):
        self.client = client
        self.anime_bot = Anime()
        super().__init__(name='anime')

    @app_commands.command(
        name="anime_busca",
        description="Faça uma pesquisa por um nome de anime"
    )
    @app_commands.describe(query='Anime query')
    async def anime_search(self, interaction: discord.Interaction, query: str):
        """
        Faça uma pesquisa por um nome de anime
        """
        await interaction.response.defer()
        async with interaction.channel.typing():
            results = self.anime_bot.search_anime(query)

        if not results:
            return await interaction.followup.send("Oops, houve um erro ao buscar pelo seu anime...")

        embed = discord.Embed(
            title=i(interaction, "Results for {}").format(query),
            colour=discord.Color.blurple()
        )
        for result in results[:5]:
            embed.add_field(name=result['title'], value=result['synopsis'])
        await interaction.followup.send(embed=embed)

    @app_commands.command(
        name="anime_info",
        description="Veja informações do anime buscado com MyAnimeList"
    )
    @app_commands.describe(query='Anime query')
    async def get_anime(self, interaction: discord.Interaction, query: str):
        """
        Veja informações do anime buscado com MyAnimeList
        """
        await interaction.response.defer()
        async with interaction.channel.typing():
            try:
                result = self.anime_bot.get_anime(int(query))
            except:
                try:
                    search_result = self.anime_bot.search_anime(query)[0]
                    result = self.anime_bot.get_anime(int(search_result["mal_id"]))
                except Exception as e:
                    logging.warning(e, exc_info=True)
                    return await interaction.send(i(interaction, "Something went wrong when searching for your anime"))

        embed = discord.Embed(
            title=result.title,
            description=result.synopsis,
            colour=discord.Color.blurple(),
            url=result.url
        )
        embed.set_image(url=result.image_url)
        embed.add_field(name='Type', value=result.type)
        embed.add_field(name='Genres', value=', '.join(result.genres))
        embed.add_field(name='Score', value=result.score)
        embed.add_field(name='Num episodes', value=result.episodes)
        await interaction.followup.send(embed=embed)
