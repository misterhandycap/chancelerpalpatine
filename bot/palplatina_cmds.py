from datetime import datetime

import discord
from discord.ext import commands

from bot.economy.palplatina import Palplatina


class PalplatinaCmds(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.palplatina = Palplatina()

    @commands.command()
    async def daily(self, ctx):
        user = await self.palplatina.give_daily(ctx.message.author.id, ctx.message.author.name)
        if not user:
            palplatinasrejeitou = discord.Embed(
                title='Daily!',
                description = f'Você já pegou seu daily hoje. Ambição leva ao lado sombrio da força, gosto disso.',
                colour = discord.Color.greyple(),
                timestamp = ctx.message.created_at
            )
            palplatinasrejeitou.set_thumbnail(url='https://cdn.discordapp.com/attachments/307920220406808576/800525198687731742/palplatina.png')    

            await ctx.send(embed=palplatinasrejeitou)
        else:
            palplatinasrecebeu = discord.Embed(
                title = 'Daily!',
                description = f'Você recebeu 300 palplatinas, faça bom uso',
                colour = discord.Color.greyple(),
                timestamp = ctx.message.created_at
            )
            palplatinasrecebeu.set_thumbnail(url='https://cdn.discordapp.com/attachments/307920220406808576/800525198687731742/palplatina.png')
            await ctx.send(embed=palplatinasrecebeu)

    @commands.command(aliases=['conta', 'atm', 'palplatina'])
    async def banco(self, ctx):
        currency = await self.palplatina.get_currency(ctx.message.author.id)
        
        moedas = discord.Embed(
            title='Daily!',
            description=f'{ctx.author.mention} possui {currency} palplatinas.',
            colour=discord.Color.greyple(),
            timestamp=ctx.message.created_at
        )
        moedas.set_thumbnail(
            url='https://cdn.discordapp.com/attachments/307920220406808576/800525198687731742/palplatina.png')
        await ctx.send(embed=moedas)
