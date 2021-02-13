from datetime import datetime

import discord
from discord.ext import commands

from bot.economy.palplatina import Palplatina
from bot.utils import PaginatedEmbedManager


class PalplatinaCmds(commands.Cog):
    """
    Economia
    """

    def __init__(self, client):
        self.client = client
        self.palplatina = Palplatina()
        self.shop_paginated_embed_manager = PaginatedEmbedManager(
            self.client, self._build_shop_embed)

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
        await self.shop_paginated_embed_manager.send_embed(
            await self._build_shop_embed(page_number), page_number, ctx)

    async def _build_shop_embed(self, page_number):
        profile_items, last_page = await self.palplatina.get_available_items(page_number-1)
        embed = discord.Embed(
            title='Lojinha do Chanceler',
            description='Navegue pelos itens disponíveis'
        )
        self.shop_paginated_embed_manager.last_page = last_page
        for profile_item in profile_items:
            embed.add_field(name=profile_item.name, value=profile_item.price)
        return embed
    
    @commands.command(aliases=['items'])
    async def itens(self, ctx):
        """
        Veja os itens que você comprou
        """
        profile_items = await self.palplatina.get_user_items(ctx.message.author.id)
        embed = discord.Embed(
            title='Seus itens adquiridos',
            description='Navegue pelos sues itens'
        )
        for profile_item in profile_items:
            embed.add_field(name=profile_item.name, value=profile_item.price)
        await ctx.send(embed=embed)

    @commands.command(aliases=['buy'])
    async def comprar(self, ctx, *, profile_item_name):
        """
        Compre um item para seu perfil

        Informe o nome do item que deseja comprar. Para que possa fazê-lo, é necessário \
            que tenha palplatinas suficientes.
        """
        result = await self.palplatina.buy_item(ctx.message.author.id, profile_item_name)
        await ctx.send(result)
