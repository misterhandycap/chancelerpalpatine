import discord
import random
import json
import os
from discord.ext import commands
from client import client

@client.event
async def on_member_join(member):
    with open('users.json', 'r') as f:
        users = json.load(f)

        await update_data(users, member)

    with open('users.json' 'w') as f:
        json.dump(users, f)

@client.event
async def on_message(message):
    with open('users.json', 'r') as f:
        users = json.load(f)

        await update_data(users, message.author)
        await add_xp(users, message.author, 5)
        await level_up(users, message.author, message.channel)

    with open('users.json', 'w') as f:
        json.dump(users, f)

async def update_data(users, user):
    if not user.id in users:
        users[user.id] = {}
        users[user.id]['experiencia'] = 0
        users[user.id]['level'] = 1

async def add_xp(users, user, xp):
    users[user.id]['experiencia'] += xp

async def level_up(users, user, channel):
    experiencia = users[user.id]['experiencia']
    level_start = users[user.id]['level']
    level_end = int(experiencia **(1/4))

    if level_start < level_end:
        await client.send_message(channel, '{} se tornou mais valioso ao subir ao nível {}'.format(user.mention, level_end))
        users[user.id]['level'] = level_end

    @client.command(aliases=['nível'])
    async def level(ctx):
        current_lvl = users[f'{member.id}']['level']
        current_xp = users[f'{member.id}']['experiencia']
        member = ctx.message.author
        member_icon = member.avatar_url
        guild = client.get_guild(684329516385959945)
        with open('users.json', 'r') as f:
            json.dump(users, f)
        lvl_embed=discord.Embed(title=" " + member + " ♥ " + guild.name, color=0xcc2800)
        lvl_embed.set_thumbnail(member_icon)
        lvl_embed.add_field(name="🔻 " + current_lvl + " LVL", value="Gain more xp to level up.", inline=False)
        lvl_embed.add_field(name="🔺 " + current_xp + " XP", value="Type in chat fore more xp.", inline=True)
        print('printira')
        await ctx.send(embed=lvl_embed)
