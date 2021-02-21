from bot.across_the_stars.planets import Planets
import discord
from discord.ext import commands
import os
from datetime import datetime
from bot.across_the_stars.vote import Vote


class AcrossTheStarsCmds(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.planets = Planets()
        self.vote = Vote()

    @commands.command(aliases=['planets'])
    async def planetas(self, ctx, *, args):
        discord_file = discord.File(
            os.path.join('bot', 'images', 'arnaldo-o-hutt.gif'), 'hutt.gif')

        planets = await self.planets.list_of_planets(region=args)

        embed = discord.Embed(
            title='Empório do Arnaldo',
            description='Se torne o senador para um planeta',
            colour=discord.Color.green()
        )
        embed.set_thumbnail(url="attachment://hutt.gif")
        for planet in planets:
            embed.add_field(
                name=planet.name,
                value=f'Preço: {planet.price}\nRegião: {planet.region.capitalize()}\nClima: {planet.climate.capitalize()}\nCircunferência: {planet.circuference}'
            )

        await ctx.reply(embed=embed, file=discord_file,
        mention_author=False)

    @commands.command(aliases=['votar'])
    async def voto(self, ctx, *, args):
        args = options.split(';')
        
        embed = discord.Embed(
            title='Voto',
            description='Vote na proposta de um colega!',
            value='Eu amo democracia! {} convocou uma votação! A proposta é {}, e as opções são {}'.format(
                message.author.mention, args[0], args[1:]),
            colour=discord.Color.red()
        )
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/676574583083499532/752314249610657932/1280px-Flag_of_the_Galactic_Republic.png")

        await ctx.send(embed=embed)

        