import os
from datetime import datetime

import discord
from discord.ext import commands

from bot.economy.palplatina import Palplatina
from bot.i18n import _, change_language
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
                title = _('Daily!'),
                description = _('You have received 300 palplatinas, enjoy!'),
                colour = discord.Color.greyple(),
                timestamp = ctx.message.created_at
            )
        else:
            palplatinas_embed = discord.Embed(
                title=_('Daily!'),
                description=_('You have alredy collected your daily today. Ambition leads to the dark side of the Force, I like it.'),
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
            title=_('Daily!'),
            description=_('{username} has {currency} palplatinas.').format(
                username=ctx.author.mention,
                currency=currency
            ),
            colour=discord.Color.greyple(),
            timestamp=ctx.message.created_at
        )
        embed.set_thumbnail(
            url='https://cdn.discordapp.com/attachments/307920220406808576/800525198687731742/palplatina.png')
        await ctx.send(embed=embed)

    @commands.command(aliases=['shop', 'lojinha'])
    async def loja(self, ctx, lang, page_number=1):
        """
        Veja os itens disponíveis para serem adquiridos
        """
        change_language(lang)
        discord_file = discord.File(
            os.path.join('bot', 'images', 'arnaldo-o-hutt.gif'), 'hutt.gif')
        await self.shop_paginated_embed_manager.send_embed(
            await self._build_shop_embed(page_number), page_number,
            ctx, discord_file
        )

    async def _build_shop_embed(self, page_number):
        profile_items, last_page = await self.palplatina.get_available_items(page_number-1)
        embed = discord.Embed(
            title=_("Arnaldo's Emporium"),
            description=_('Browse through all available items'),
            colour=discord.Color.green()
        )
        embed.set_thumbnail(url="attachment://hutt.gif")
        self.shop_paginated_embed_manager.last_page = last_page
        for profile_item in profile_items:
            embed.add_field(
                name=profile_item.name,
                value=f'{_("Price")}: {profile_item.price}\n{_("Type")}: {profile_item.type.name.capitalize()}'
            )
        return embed
    
    @commands.command(aliases=['items'])
    async def itens(self, ctx):
        """
        Veja os itens que você comprou
        """
        profile_items = await self.palplatina.get_user_items(ctx.message.author.id)
        embed = discord.Embed(
            title=_('Your acquired items'),
            description=_('Browse through all your acquired items'),
            colour=discord.Color.green()
        )
        for profile_item in profile_items:
            embed.add_field(
                name=profile_item.name,
                value=profile_item.type.name.capitalize()
            )
        await ctx.send(embed=embed)

    @commands.command(aliases=['buy'])
    async def comprar(self, ctx, *, profile_item_name):
        """
        Compre um item para seu perfil

        Informe o nome do item que deseja comprar. Para que possa fazê-lo, é necessário \
            que tenha palplatinas suficientes.
        """
        profile_item = await self.palplatina.get_item(profile_item_name)
        if not profile_item:
            return await ctx.send(_('Item not found'))
        
        embed = discord.Embed(
            title=_('Buy item'),
            description=profile_item.name
        )
        discord_file = None
        if profile_item.get_file_contents():
            discord_file = discord.File(profile_item.file_path, 'item.png')
            embed.set_thumbnail(url="attachment://item.png")
        embed.set_author(name=ctx.author)
        embed.add_field(name=_('Price'), value=profile_item.price)
        embed.add_field(name=_('Your palplatinas'), value=await self.palplatina.get_currency(ctx.message.author.id))
        
        message = await ctx.send(embed=embed, file=discord_file)
        await message.add_reaction('✅')
        await message.add_reaction('🚫')

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        confirm_emoji = '✅'
        cancel_emoji = '🚫'
        valid_emojis = [confirm_emoji, cancel_emoji]
        if not reaction.message.embeds:
            return
        embed = reaction.message.embeds[0]
        if not (embed.title == _('Buy item') and str(user) == embed.author.name):
            return

        emoji = str(reaction)
        if emoji not in valid_emojis:
            return

        if emoji == confirm_emoji:
            result = await self.palplatina.buy_item(user.id, embed.description)
        else:
            result = _('Operation canceled')
        
        await reaction.message.channel.send(content=f'{embed.author.name}: {result}')
