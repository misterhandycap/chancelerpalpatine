import json
import os
import random
import time
from datetime import datetime, timedelta

import discord
from discord.ext import commands

from bot.models.user import User
from bot.models.xp_point import XpPoint
from bot.servers import cache
from bot.utils import i, paginate


class LevelCog(commands.Cog):
    """
    Comandos de nível do bot
    """

    def __init__(self, client):
        self.client = client
    
    def sabio(self, ctx, msg):
        if 'b' in msg:
            start = msg.index('b') + 2
    
            msg = msg[start:]
            if len(msg)>4:
                gender = msg[0]
                name = msg[2:]
                
                return f"Já ouviu a história de Darth {name}, {gender} sábi{gender}?"
            return i(ctx, "Did you ever hear the tragedy of Darth Plagueis, the Wise?")

    @commands.Cog.listener()
    async def on_message(self, message):
        await self._send_autoreply(message)
        
        if (message.content.lower().startswith('você é muito sábi') or 
                message.content.lower().startswith('tão sábi') or 
                message.content.lower().startswith('sábi')):
            await message.channel.send(self.sabio(message, message.content))

        if message.author.bot or not message.guild:
            return
        
        xp_points = await self.update_data(message.author, message.guild.id)
        exp = random.randint(5, 15)
        await self.add_xp(xp_points, exp)
        await self.level_up(xp_points, message)
        await XpPoint.save(xp_points)

    async def _send_autoreply(self, message):
        autoreply_config = cache.get_autoreply_to_message(
            message.guild.id, message.content.lower())
        if not autoreply_config:
            return
        
        if autoreply_config.reply:
            await message.channel.send(autoreply_config.reply)
        if autoreply_config.reaction:
            try:
                await message.add_reaction(autoreply_config.reaction)
            except:
                pass
        if autoreply_config.image_url:
            await message.channel.send(autoreply_config.image_url)

    async def update_data(self, user, server_id):
        xp_points = await XpPoint.get_by_user_and_server(user.id, server_id)
        if not xp_points:
            xp_points = XpPoint()
            xp_points.user = await User.get(user.id) or User(id=user.id, name=user.name)
            xp_points.server_id = server_id
            xp_points.points = 0
            xp_points.level = 1
            xp_points.updated_at = datetime.utcnow()
        return xp_points

    async def add_xp(self, xp_points, xp):
        if (xp_points.updated_at - datetime.utcnow()).seconds > 40:
            xp_points.points += xp
            xp_points.updated_at = datetime.utcnow()

    async def level_up(self, xp_points, message):
        experiencia = xp_points.points
        level_start = xp_points.level
        level_end = int(experiencia **(1/4))
        bot_env = os.environ.get("ENV", 'dev')

        if level_start < level_end:
            if bot_env == 'prod':
                await message.channel.send(
                    '{} subiu ao nível {}! Assistiremos sua carreira com grande interesse.'.format(
                        message.author.mention, level_end))
            xp_points.level = level_end

    @commands.command(aliases=['nivel'])
    async def level(self, ctx, user: discord.User=None):
        """
        Mostra o nível de usuário

        Passe um usuário para ver seu nível. Se não for passado nenhum usuário, \
            o seu nível de usuário será retornado.
        """
        selected_user = user if user else ctx.author
        xp_point = await XpPoint.get_by_user_and_server(selected_user.id, ctx.message.guild.id)
        if not xp_point:
            xp_point = XpPoint(level=0, points=0)

        levelbed = discord.Embed(
            title='Nível',
            description=f'{selected_user.mention} se encontra atualmente no nível {xp_point.level} com {xp_point.points}',
            colour=discord.Color.red(),
            timestamp=ctx.message.created_at
        )
        levelbed.set_thumbnail(url='https://cdn.discordapp.com/attachments/676574583083499532/752314249610657932/1280px-Flag_of_the_Galactic_Republic.png')
        await ctx.send(embed=levelbed)

    @commands.command(aliases=['board'])
    async def rank(self, ctx, page_number: int=1):
        """
        Mostra a tabela de niveis de usuários em ordem de maior pra menor
        """
        page_size = 5
        xp_points = await XpPoint.list_by_server(ctx.message.guild.id)

        rank, last_page = paginate(xp_points, page_number, page_size)

        msg = '\n'.join([f'* **{r.user.name}** - {r.points}' for r in rank])
        msg += f'\n\nPágina {page_number} de {last_page}'

        await ctx.send(msg)
