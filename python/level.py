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

    with open('users.json', 'w') as f:
        json.dump(users, f)

@client.event
async def on_message(message):
    with open('users.json', 'r') as f:
        users = json.load(f)

        if message.author.bot:
            return

        else:

            await update_data(users, message.author)
            exp = random.randint(5, 15)
            await add_xp(users, message.author, exp)
            await level_up(users, message.author, message.channel)

        with open('users.json', 'w') as f:
            json.dump(users, f)

        await client.process_commands(message)

async def update_data(users, user):
    if not str(user.id) in users:
        users[str(user.id)] = {}
        users[str(user.id)]['experiencia'] = 0
        users[str(user.id)]['level'] = 1

async def add_xp(users, user, xp):
    users[str(user.id)]['experiencia'] += xp

async def level_up(users, user, channel):
    experiencia = users[str(user.id)]['experiencia']
    level_start = users[str(user.id)]['level']
    level_end = int(experiencia **(1/4))

    if level_start < level_end:
        await channel.send('{} se tornou mais valioso ao subir ao nível {}'.format(user.mention, level_end))
        users[str(user.id)]['level'] = level_end
        await client.process_commands(message)
