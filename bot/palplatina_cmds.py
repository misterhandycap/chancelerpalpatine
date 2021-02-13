from datetime import datetime

import discord
from discord.ext import commands

from bot.economy.palplatina import Palplatina


class PalplatinaCmds(commands.Cog):
    """
    Economia
    """

    def __init__(self, client):
        self.client = client
        self.palplatina = Palplatina()

    @commands.command()
    async def daily(self, ctx):
        """
        Receba sua recompensa diária em Palplatinas 🤑
        """
        received_daily, user = await self.palplatina.give_daily(
            ctx.message.author.id, ctx.message.author.name)
        if received_daily:
            palplatinas_embed = discord.Embed(
                title = 'Daily!',
                description = f'Você recebeu 300 palplatinas, faça bom uso.',
                colour = discord.Color.greyple(),
                timestamp = ctx.message.created_at
            )
        else:
            palplatinas_embed = discord.Embed(
                title='Daily!',
                description=f'Você já pegou seu daily hoje. Ambição leva ao lado sombrio da Força, gosto disso.',
                colour=discord.Color.greyple(),
                timestamp=user.daily_last_collected_at
            )
        palplatinas_embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/307920220406808576/800525198687731742/palplatina.png')    
        await ctx.send(embed=palplatinas_embed)

    @commands.command(aliases=['conta', 'atm', 'palplatina'])
    async def banco(self, ctx):
        """
        Veja seu saldo de Palplatinas 💰
        """
        currency = await self.palplatina.get_currency(ctx.message.author.id)
        
        embed = discord.Embed(
            title='Daily!',
            description=f'{ctx.author.mention} possui {currency} palplatinas.',
            colour=discord.Color.greyple(),
            timestamp=ctx.message.created_at
        )
        embed.set_thumbnail(
            url='https://cdn.discordapp.com/attachments/307920220406808576/800525198687731742/palplatina.png')
        await ctx.send(embed=embed)

    @commands.command(aliases=['shop', 'lojinha'])
    async def loja(self, ctx, page_number=1):
        """
        Veja os itens disponíveis para serem adquiridos
        """
        profile_items = await self.palplatina.get_available_items(page_number-1)
        embed = discord.Embed(
            title='Lojinha do Chanceler',
            description='Navegue pelos itens disponíveis'
        )
        for profile_item in profile_items:
            embed.add_field(name=profile_item.name, value=profile_item.price)
        await ctx.send(embed=embed)
    
    @commands.command(aliases=['items'])
    async def itens(self, ctx):
        """
        Veja os itens que você comprou
        """
        profile_items = await self.palplatina.get_user_items(ctx.message.author.id)
        items_names = [item.name for item in profile_items]
        if items_names == []:
            return await ctx.send('Você não tem nenhum item')
        await ctx.send(', '.join(items_names))

    @commands.command(aliases=['buy'])
    async def comprar(self, ctx, profile_item_id):
        """
        Compre um item para seu perfil
        """
        result = await self.palplatina.buy_item(ctx.message.author.id, profile_item_id)
        await ctx.send(result)
