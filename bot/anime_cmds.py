import logging

import discord
from discord.ext import commands
from discord_slash import cog_ext
from discord_slash.utils.manage_commands import create_option

from bot.anime.anime import Anime
from bot.utils import i


class AnimeCog(commands.Cog):
    """
    Comandos de anime
    """

    def __init__(self, client):
        self.client = client
        self.anime_bot = Anime()

    @cog_ext.cog_slash(
        name="anime_busca",
        description="Faça uma pesquisa por um nome de anime",
        options=[
            create_option(name="query", description="Anime query", option_type=3, required=True)
        ]
    )
    async def anime_search(self, ctx, query):
        """
        Faça uma pesquisa por um nome de anime
        """
        await ctx.defer()
        async with ctx.channel.typing():
            results = self.anime_bot.search_anime(query)

        if not results:
            return await ctx.send("Oops, houve um erro ao buscar pelo seu anime...")

        embed = discord.Embed(
            title=i(ctx, "Results for {}").format(query),
            colour=discord.Color.blurple()
        )
        for result in results[:5]:
            embed.add_field(name=result['title'], value=result['synopsis'])
        await ctx.send(embed=embed)

    @cog_ext.cog_slash(
        name="anime_info",
        description="Veja informações do anime buscado com MyAnimeList",
        options=[
            create_option(name="query", description="Anime query", option_type=3, required=True)
        ]
    )
    async def get_anime(self, ctx, query):
        """
        Veja informações do anime buscado com MyAnimeList
        """
        await ctx.defer()
        async with ctx.channel.typing():
            try:
                result = self.anime_bot.get_anime(int(query))
            except:
                try:
                    search_result = self.anime_bot.search_anime(query)[0]
                    result = self.anime_bot.get_anime(int(search_result["mal_id"]))
                except Exception as e:
                    logging.warning(e, exc_info=True)
                    return await ctx.send(i(ctx, "Something went wrong when searching for your anime"))

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
        await ctx.send(embed=embed)

    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f'{i(ctx, "Usage")}: `{self.client.command_prefix}{ctx.command.name} QUERY`')
