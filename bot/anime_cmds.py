import logging

import discord

from bot import client
from bot.anime.anime import Anime

@client.command(aliases=['busca_anime', 'buscar_anime', 'anime_buscar'])
async def anime_busca(ctx, *args):
    query = ' '.join(args)
    if not query:
        return await ctx.send("Uso: `cp!anime_busca BUSCA`")
    await ctx.trigger_typing()
    anime_bot = Anime()
    results = anime_bot.search_anime(query)

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

@client.command()
async def anime(ctx, *args):
    query = ' '.join(args)
    if not query:
        return await ctx.send("Uso: `cp!anime BUSCA`")
    await ctx.trigger_typing()
    anime_bot = Anime()
    try:
        result = anime_bot.get_anime(int(query))
    except:
        try:
            search_result = anime_bot.search_anime(query)[0]
            result = anime_bot.get_anime(int(search_result["mal_id"]))
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
