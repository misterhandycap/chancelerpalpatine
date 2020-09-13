import discord
import random
import json
import os
import time
from discord.ext import commands
from bot import client

@client.event
async def on_member_join(member):
    with open('users.json', 'r') as f:
        users = json.load(f)

        await update_data(users, member)

    with open('users.json', 'w') as f:
        json.dump(users, f)

@client.event
async def on_message(message):
    if message.content.lower().startswith('odeio'):
        await message.channel.send('Sim, deixe o ódio fluir por você... <:sheev:735473486046298173>')

    if message.content.lower().startswith('ban'):
        await message.channel.send('Mate-o, mate-o agora...')

    if message.content.lower().startswith('i shouldnt'):
        await message.channel.send('DEW IT!')

    if message.content.lower().startswith('i shouldn\'t'):
        await message.channel.send('DEW IT!')

    if message.content.lower().startswith('-poll'):
        await message.channel.send('Eu amo democracia!')

    if message.content.lower().startswith('votação'):
        await message.channel.send('Eu amo democracia!')

    if message.content.lower().startswith('voto'):
        await message.channel.send('Eu amo democracia!')

    if message.content.lower().startswith('democracia'):
        await message.channel.send('Eu amo democracia!')

    if message.content.lower().startswith('estou muito fraco'):
        await message.channel.send('PODER ILIMITADOOOOOO!')

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
        users[str(user.id)]['ultima_mesg'] = 0
        users[str(user.id)]['id'] = user.id

async def add_xp(users, user, xp):
    if time.time() - users[str(user.id)]['ultima_mesg'] >40:
        users[str(user.id)]['experiencia'] += xp
        users[str(user.id)]['ultima_mesg'] = time.time()
    else:
        return

async def level_up(users, user, channel):
    experiencia = users[str(user.id)]['experiencia']
    level_start = users[str(user.id)]['level']
    level_end = int(experiencia **(1/4))

    if level_start < level_end:


        await channel.send('{} subiu ao nível {}! Assistiremos sua carreira com grande interesse.'.format(user.mention, level_end))
        users[str(user.id)]['level'] = level_end

@client.command(aliases=['nivel'])
async def level(ctx):
    user_id = str(ctx.author.id)
    with open('users.json', 'r') as f:
        users = json.load(f)

        levelbed = discord.Embed(title='Nível', description=f'{ctx.author.mention} se encontra atualmente no nível {users[str(ctx.author.id)]["level"]}', colour=discord.Color.red(), timestamp=ctx.message.created_at)
        levelbed.set_thumbnail(url='https://cdn.discordapp.com/attachments/676574583083499532/752314249610657932/1280px-Flag_of_the_Galactic_Republic.png')
        await ctx.send(embed=levelbed)

@client.command(aliases=['board'])
async def rank(ctx):
    user_id = str(ctx.author.id)
    with open('users.json', 'r') as f:
        users = json.load(f)

    rank = sorted(users.items(), key=lambda x: x[1]['experiencia'], reverse=True)
    msg = '\n '.join([str(x[1]['experiencia']) for x in rank])

    await ctx.send(msg)
