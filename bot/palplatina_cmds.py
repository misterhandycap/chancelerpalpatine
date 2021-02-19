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
        await ctx.reply(embed=palplatinas_embed,
        mention_author=False)

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
        discord_file = discord.File(
            os.path.join('bot', 'images', 'arnaldo-o-hutt.gif'), 'hutt.gif')
        await self.shop_paginated_embed_manager.send_embed(
            await self._build_shop_embed(page_number), page_number,
            ctx, discord_file
        )

    async def _build_shop_embed(self, page_number):
        profile_items, last_page = await self.palplatina.get_available_items(page_number-1)
        embed = discord.Embed(
            title='Empório do Arnaldo',
            description='Navegue pelos itens disponíveis',
            colour=discord.Color.green()
        )
        embed.set_thumbnail(url="attachment://hutt.gif")
        self.shop_paginated_embed_manager.last_page = last_page
        for profile_item in profile_items:
            embed.add_field(
                name=profile_item.name,
                value=f'Preço: {profile_item.price}\nTipo: {profile_item.type.name.capitalize()}'
            )
        return embed
    
    @commands.command(aliases=['items'])
    async def itens(self, ctx):
        """
        Veja os itens que você comprou
        """
        profile_items = await self.palplatina.get_user_items(ctx.message.author.id)
        embed = discord.Embed(
            title='Seus itens adquiridos',
            description='Navegue pelos seus itens',
            colour=discord.Color.green()
        )
        for profile_item in profile_items:
            embed.add_field(
                name=profile_item.name,
                value=profile_item.type.name.capitalize()
            )
        await ctx.reply(embed=embed,
        mention_author=False)

    @commands.command(aliases=['buy'])
    async def comprar(self, ctx, *, profile_item_name):
        """
        Compre um item para seu perfil

        Informe o nome do item que deseja comprar. Para que possa fazê-lo, é necessário \
            que tenha palplatinas suficientes.
        """
        profile_item = await self.palplatina.get_item(profile_item_name)
        if not profile_item:
            return await ctx.reply('Item não encontrado',
            mention_author=False)
        
        embed = discord.Embed(
            title='Comprar item',
            description=profile_item.name
        )
        discord_file = None
        if profile_item.get_file_contents():
            discord_file = discord.File(profile_item.file_path, 'item.png')
            embed.set_thumbnail(url="attachment://item.png")
        embed.set_author(name=ctx.author)
        embed.add_field(name='Preço', value=profile_item.price)
        embed.add_field(name='Suas palplatinas', value=await self.palplatina.get_currency(ctx.message.author.id))
        
        message = await ctx.reply(embed=embed, file=discord_file,
        mention_author=False)
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
        if not (embed.title == 'Comprar item' and str(user) == embed.author.name):
            return

        emoji = str(reaction)
        if emoji not in valid_emojis:
            return

        await ctx.send('s')
