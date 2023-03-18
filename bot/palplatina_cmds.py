import os
from datetime import datetime
from typing import Literal, Optional

import discord
from discord.ui import button
from discord import app_commands

from bot.economy.exceptions import EconomyException
from bot.economy.item import Item
from bot.economy.palplatina import Palplatina
from bot.models.exceptions import ProfileItemException
from bot.utils import i, PaginatedEmbedManager, PersonalView


class PalplatinaCmds(app_commands.Group):
    """
    Economia
    """

    def __init__(self, client):
        self.client = client
        self.palplatina = Palplatina()
        self.item_bot = Item()
        self.shop_paginated_embed_manager = PaginatedEmbedManager(self._build_shop_embed)
        super().__init__(name='palplatina')

    @app_commands.command(
        name="daily",
        description="Receba sua recompensa diária em Palplatinas 🤑"
    )
    async def daily(self, interaction: discord.Interaction):
        """
        Receba sua recompensa diária em Palplatinas 🤑
        """
        received_daily, user = await self.palplatina.give_daily(
            interaction.user.id, interaction.user.name)
        if received_daily:
            palplatinas_embed = discord.Embed(
                title=i(interaction, 'Daily!'),
                description=i(interaction, 'You have received 300 palplatinas, enjoy!'),
                colour=discord.Color.greyple(),
                timestamp=datetime.utcnow()
            )
        else:
            palplatinas_embed = discord.Embed(
                title=i(interaction, 'Daily!'),
                description=i(interaction, 'You have alredy collected your daily today. Ambition leads to the dark side of the Force, I like it.'),
                colour=discord.Color.greyple(),
                timestamp=user.daily_last_collected_at
            )
        palplatinas_embed.set_thumbnail(url='https://cdn.discordapp.com/attachments/307920220406808576/800525198687731742/palplatina.png')    
        palplatinas_embed.set_author(name=interaction.user)
        await interaction.response.send_message(embed=palplatinas_embed)

    @app_commands.command(
        name="banco",
        description="Veja seu saldo de Palplatinas 💰"
    )
    async def get_balance(self, interaction: discord.Interaction):
        """
        Veja seu saldo de Palplatinas 💰
        """
        currency = await self.palplatina.get_currency(interaction.user.id)
        
        embed = discord.Embed(
            title=i(interaction, 'Daily!'),
            description=i(interaction, '{username} has {currency} palplatinas.').format(
                username=interaction.user.mention,
                currency=currency
            ),
            colour=discord.Color.greyple()
        )
        embed.set_thumbnail(
            url='https://cdn.discordapp.com/attachments/307920220406808576/800525198687731742/palplatina.png')
        await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name="loja",
        description="Veja os itens disponíveis para serem adquiridos"
    )
    @app_commands.describe(search_query='Busca')
    async def shop(self, interaction: discord.Interaction, search_query: Optional[str]=''):
        """
        Veja os itens disponíveis para serem adquiridos
        """
        page_number = 1
        discord_file = discord.File(
            os.path.join('bot', 'images', 'arnaldo-o-hutt.gif'), 'hutt.gif')
        shop_embed = await self._build_shop_embed(page_number, interaction, search_query=search_query)
        await self.shop_paginated_embed_manager.send_embed(
            shop_embed, page_number, interaction,
            discord_file=discord_file, content=i(interaction, 'Results for: {}').format(search_query)
        )

    async def _build_shop_embed(self, page_number, original_message, search_query=None):
        if search_query is None:
            search_query = ': '.join(original_message.content.split(': ')[1:])
        profile_items, last_page = await self.palplatina.get_available_items(search_query, page_number-1)
        embed = discord.Embed(
            title=i(original_message, "Arnaldo's Emporium"),
            description=i(original_message, 'Browse through all available items'),
            colour=discord.Color.green()
        )
        embed.set_thumbnail(url="attachment://hutt.gif")
        self.shop_paginated_embed_manager.last_page = last_page
        for profile_item in profile_items:
            embed.add_field(
                name=profile_item.name,
                value=f'{i(original_message, "Price")}: {profile_item.price}\n{i(original_message, "Type")}: {profile_item.type.name.capitalize()}'
            )
        return embed
    
    @app_commands.command(
        name="itens",
        description="Veja os itens que você comprou"
    )
    async def items(self, interaction: discord.Interaction):
        """
        Veja os itens que você comprou
        """
        user_profile_items = await self.palplatina.get_user_items(interaction.user.id)
        embed = discord.Embed(
            title=i(interaction, 'Your acquired items'),
            description=i(interaction, 'Browse through all your acquired items'),
            colour=discord.Color.green()
        )
        for user_profile_item in user_profile_items:
            embed.add_field(
                name=user_profile_item.profile_item.name,
                value=i(interaction, 'Equipped') if user_profile_item.equipped else i(interaction, 'Not equipped')
            )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(
        name="equipar",
        description="Equipa o item fornecido"
    )
    @app_commands.describe(profile_item_name='Nome do item')
    async def equip_item(self, interaction: discord.Interaction, profile_item_name: str):
        try:
            await self.palplatina.equip_item(interaction.user.id, profile_item_name)
            return await interaction.response.send_message(i(interaction, 'Equipped'))
        except EconomyException as e:
            result = i(interaction, e.message)

    @app_commands.command(
        name="desequipar",
        description="Desequipa o item fornecido"
    )
    @app_commands.describe(profile_item_name='Nome do item')
    async def unequip_item(self, interaction: discord.Interaction, profile_item_name: str):
        try:
            await self.palplatina.unequip_item(interaction.user.id, profile_item_name)
            return await interaction.response.send_message(i(interaction, 'Not equipped'))
        except EconomyException as e:
            result = i(interaction, e.message)

    @app_commands.command(
        name="comprar",
        description="Compre um item para seu perfil"
    )
    @app_commands.describe(profile_item_name='Nome do item')
    async def buy_item(self, interaction: discord.Interaction, profile_item_name: str):
        """
        Compre um item para seu perfil

        Informe o nome do item que deseja comprar. Para que possa fazê-lo, é necessário \
            que tenha palplatinas suficientes.
        """
        profile_item = await self.palplatina.get_item(profile_item_name)
        if not profile_item:
            return await interaction.response.send_message(i(interaction, 'Item not found'))
        
        confirm_view = ConfirmView(owner=interaction.user)
        embed = discord.Embed(
            title=i(interaction, 'Buy item'),
            description=profile_item.name
        )
        discord_file = None
        if profile_item.get_file_contents():
            discord_file = discord.File(profile_item.file_path, 'item.png')
            embed.set_thumbnail(url="attachment://item.png")
        embed.set_author(name=interaction.user)
        embed.add_field(name=i(interaction, 'Price'), value=profile_item.price)
        embed.add_field(name=i(interaction, 'Your palplatinas'), value=await self.palplatina.get_currency(interaction.user.id))
        
        await interaction.response.send_message(embed=embed, file=discord_file, view=confirm_view)
        await confirm_view.wait()
        
        if confirm_view.value:
            try:
                economy_user = await self.palplatina.buy_item(interaction.user.id, embed.description)
                result = (i(interaction, 'Item bought. You now have {currency} palplatinas')
                    .format(currency=economy_user.currency)
                )
            except EconomyException as e:
                result = i(interaction, e.message)
        else:
            result = i(interaction, 'Operation canceled')
        
        await interaction.edit_original_response(content=f'{embed.author.name}: {result}', view=None)

    @app_commands.command(
        name="novo_item",
        description="Sugira um novo item a ser adicionado à loja do bot"
    )
    @app_commands.describe(
        item_type='Tipo de item',
        price='Preço',
        name='Nome do item',
        url='URL da imagem do item'
    )
    async def suggest_item(self, interaction: discord.Interaction,
                           item_type: Literal['badge', 'wallpaper'], price: int,
                           name: str, url: str):
        """
        Sugira um novo item a ser adicionado à loja do bot
        """
        try:
            profile_item = self.item_bot.build_profile_item(type=item_type, price=price, name=name)
        except ProfileItemException as e:
            return await interaction.response.send_message(i(interaction, e.message))

        moderator_confirm_view = ModeratorConfirmView()
        embed = discord.Embed(
            title=i(interaction, 'New item suggestion'),
            description=profile_item.name
        )
        embed.add_field(name=i(interaction, 'Type'), value=profile_item.type)
        embed.add_field(name=i(interaction, 'Price'), value=profile_item.price)
        embed.set_author(name=interaction.user)
        embed.set_image(url=url)
        await interaction.response.send_message(embed=embed, view=moderator_confirm_view)
        await moderator_confirm_view.wait()
        
        if moderator_confirm_view.value:
            profile_item = self.item_bot.build_profile_item(
                name=embed.description,
                price=next(int(field.value) for field in embed.fields if field.name == i(interaction, 'Price')),
                type=next(field.value for field in embed.fields if field.name == i(interaction, 'Type'))
            )
            try:
                await self.item_bot.save_profile_item(profile_item, embed.image.url)
                result = i(interaction, 'New item added to the shop!')
            except discord.HTTPException:
                result = i(interaction, 'Could not find original message 😣')
        else:
            result = i(interaction, 'Operation canceled')
        
        await interaction.edit_original_response(content=f'{embed.author.name}: {result}', view=None)

            
class ConfirmView(PersonalView):
    def __init__(self, *, owner=discord.User, timeout: Optional[float] = 180):
        self.value = None
        super().__init__(owner=owner, timeout=timeout)
    
    @button(label='Confirmar', style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, _):
        await interaction.response.defer(thinking=False)
        self.value = True
        self.stop()
        
    @button(label='Cancelar', style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, _):
        await interaction.response.defer(thinking=False)
        self.value = False
        self.stop()


class ModeratorConfirmView(ConfirmView):
    def __init__(self, *, timeout: Optional[float] = 180):
        self.moderators_ids = os.environ.get('MODERATORS_IDS', '').split(',')
        super().__init__(owner=None, timeout=timeout)
        
    def _permission_check(self, interaction: discord.Interaction):
        return str(interaction.user.id) in self.moderators_ids
    
    def _permission_denied_message(self, interaction: discord.Interaction):
        return i(interaction, "Only bot moderators may react to this message")
