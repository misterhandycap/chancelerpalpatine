import logging
from typing import TYPE_CHECKING, Optional

import discord
from discord import app_commands
from discord.ui import button, View

from bot.card_jitsu.bot import Bot
from bot.card_jitsu.game import Game
from bot.discord_helpers import i, PersonalView

if TYPE_CHECKING:
    from bot.client import BotClient


class CardJitsuCmds(app_commands.Group):
    def __init__(self, client: 'BotClient'):
        self.client = client
        self.bot = Bot()
        self.interactions = {}
        super().__init__(name="card_jitsu")
        
    @app_commands.command(
        name="jogar",
        description="Inicie uma nova partida de Desafio Ninja com alguém"
    )
    @app_commands.describe(user='Usuário contra quem quer jogar')
    async def new_game(self, interaction: discord.Interaction, user: discord.User):
        await interaction.response.defer()
        
        game_invite_view = GameInviteView(self, cmd_interaction=interaction, owner=user)
        await interaction.followup.send(
            i(interaction, '{user}: You have been invited to a game of Card-Jitsu!').format(user=user.mention),
            view=game_invite_view
        )
            
    async def start_game(self, host_interaction: discord.Interaction, guest_interaction: discord.Interaction):
        try:
            game = self.bot.new_game(host_interaction.user, guest_interaction.user)
        except Exception as e:
            return await guest_interaction.followup.send(i(guest_interaction, str(e)))
        
        await guest_interaction.followup.send(i(guest_interaction, 'Game started! Loading initial hands...'))
        
        game.player_1.avatar_bytes = await host_interaction.user.display_avatar.read()
        game.player_2.avatar_bytes = await guest_interaction.user.display_avatar.read()
        
        self.interactions[host_interaction.user.id] = host_interaction
        self.interactions[guest_interaction.user.id] = guest_interaction
        
        await self.send_hands(game)
    
    async def send_hands(self, game: Game):
        await self._send_hand(self.interactions[game.player_1.id], game)
        await self._send_hand(self.interactions[game.player_2.id], game)
    
    async def _send_hand(self, interaction: discord.Interaction, game: Game):
        hand_img = await self.bot.draw_hand(interaction.user)
        hand_view = HandView(timeout=60)
        await interaction.followup.send(file=discord.File(hand_img, 'hand.png'), view=hand_view, ephemeral=True)
        if await hand_view.wait():
            logging.info(f"User {interaction.user.id} timeout on Card-Jitsu")
            await interaction.followup.send(i(interaction, "{user} timeout").format(user=interaction.user.name))
            self.bot.end_game(game)
            del self.interactions[game.player_1.id]
            del self.interactions[game.player_2.id]
        else:
            await self._make_move(interaction, hand_view.value)
    
    async def _make_move(self, interaction: discord.Interaction, card_index: int):
        try:
            game = self.bot.make_move(interaction.user, card_index)
        except Exception as e:
            return await interaction.followup.send(i(interaction, str(e)))
        
        if not game.is_turn_over():
            return
        
        turn_img = await self.bot.draw_turn(game)
        await interaction.followup.send(file=discord.File(turn_img, 'turn.png'), ephemeral=False)
        if game.is_game_over():
            await interaction.followup.send(i(interaction, "Game over! {user} wins").format(user=game.winner.name))
            self.bot.end_game(game)
            del self.interactions[game.player_1.id]
            del self.interactions[game.player_2.id]
        else:
            await self.send_hands(game)
                

class GameInviteView(PersonalView):
    def __init__(self, app_group: CardJitsuCmds, cmd_interaction: discord.Interaction, owner: discord.User, *, timeout: Optional[float] = None):
        self.value: bool
        self.app_group = app_group
        self.cmd_interaction = cmd_interaction
        super().__init__(owner=owner, timeout=timeout)
        
    @button(label="Aceitar", style=discord.ButtonStyle.green)
    async def accept(self, interaction: discord.Interaction, _):
        await interaction.response.defer(thinking=False)
        await self.app_group.start_game(self.cmd_interaction, interaction)
        
    @button(label="Rejeitar", style=discord.ButtonStyle.secondary)
    async def reject(self, interaction: discord.Interaction, _):
        await interaction.followup.send(i(interaction, "Game aborted"))


class HandView(View):
    def __init__(self, *, timeout: Optional[float] = None):
        self.value: int
        super().__init__(timeout=timeout)
        
    @button(label="Primeira carta")
    async def first_card(self, interaction: discord.Interaction, _):
        await interaction.response.defer(thinking=True)
        self.value = 0
        self.stop()
        
    @button(label="Segunda carta")
    async def second_card(self, interaction: discord.Interaction, _):
        await interaction.response.defer(thinking=True)
        self.value = 1
        self.stop()
        
    @button(label="Terceira carta")
    async def third_card(self, interaction: discord.Interaction, _):
        await interaction.response.defer(thinking=True)
        self.value = 2
        self.stop()
        
    @button(label="Quarta carta")
    async def forth_card(self, interaction: discord.Interaction, _):
        await interaction.response.defer(thinking=True)
        self.value = 3
        self.stop()
        
    @button(label="Quinta carta")
    async def fifth_card(self, interaction: discord.Interaction, _):
        await interaction.response.defer(thinking=True)
        self.value = 4
        self.stop()
