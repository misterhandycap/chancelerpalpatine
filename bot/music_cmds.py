import os

import discord
from discord.ext import commands


class MusicCog(commands.Cog):
    """
    Música
    """

    def __init__(self, client):
        self.client = client

    @commands.command()
    async def join(self, ctx, *, channel: discord.VoiceChannel):
        """
        Conecta o bot ao canal de voz fornecido
        """

        if ctx.voice_client is not None:
            return await ctx.voice_client.move_to(channel)

        await channel.connect()

    @commands.command()
    async def play(self, ctx):
        """
        Toca a música teste
        """
        source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(os.environ.get("SONG_PATH")))
        ctx.voice_client.play(source, after=lambda e: print('Player error: %s' % e) if e else None)

        await ctx.send('Tocando música teste')
