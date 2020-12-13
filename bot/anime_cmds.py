import logging

import discord
from discord.ext import commands

from bot.anime.anime import Anime


class AnimeCog(commands.Cog):
    """
    Comandos de anime
    """

    def __init__(self, client):
        self.client = client
        self.anime_bot = Anime()

    @commands.command(aliases=['busca_anime', 'buscar_anime', 'anime_buscar'])
    async def anime_busca(self, ctx, *args):
        """
        Faça uma pesquisa por um nome de anime
        """
        query = ' '.join(args)
        if not query:
            return await ctx.send("Uso: `cp!anime_busca BUSCA`")
        await ctx.trigger_typing()
        results = self.anime_bot.search_anime(query)

        if not results:
            return await ctx.send("Oops, houve um erro ao buscar pelo seu anime...")

        embed = discord.Embed(
            title=f'Resultados por "{query}"',
            colour=discord.Color.blurple(),
            timestamp=ctx.message.created_at
        )
        for result in results[:5]:
            embed.add_field(name=result['title'], value=result['synopsis'])
        await ctx.send(embed=embed)

    @commands.command()
    async def anime(self, ctx, *args):
        """
        Veja informações do anime buscado com MyAnimeList
        """
        query = ' '.join(args)
        if not query:
            return await ctx.send("Uso: `cp!anime BUSCA`")
        await ctx.trigger_typing()
        try:
            result = self.anime_bot.get_anime(int(query))
        except:
            try:
                search_result = self.anime_bot.search_anime(query)[0]
                result = self.anime_bot.get_anime(int(search_result["mal_id"]))
            except Exception as e:
                logging.warning(e, exc_info=True)
                return await ctx.send("Oops, houve um erro ao buscar pelo seu anime...")

        embed = discord.Embed(
            title=result.title,
            description=result.synopsis,
            colour=discord.Color.blurple(),
            timestamp=ctx.message.created_at,
            url=result.url
        )
        embed.set_image(url=result.image_url)
        embed.add_field(name='Type', value=result.type)
        embed.add_field(name='Genres', value=', '.join(result.genres))
        embed.add_field(name='Score', value=result.score)
        embed.add_field(name='Num episodes', value=result.episodes)
        await ctx.send(embed=embed)
