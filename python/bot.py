import discord
import random
import json
import os
from discord.ext import commands

client = discord.Client()

client = commands.Bot(command_prefix = 'cp!')

@client.check
async def globally_block_dms(ctx):
    return ctx.guild is not None

@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.online, activity=discord.Game(f'Planejando uma ordem surpresa'))
    print('É bom te ver, mestre Jedi.')

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

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredPermissions):
        await ('Parece que você não tem poder aqui, Jedi, cheque com os mestres do Conselho e volte mais tarde.')

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send('Esta ordem não existe, agora se me der licença...')

@client.command()
async def ping(ctx):
    await ctx.send(f'Pong... {round(client.latency * 1000)}ms')

@client.command(aliases=['limpar', 'clean'])
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount=5+1):
    await ctx.channel.purge(limit=amount)

@client.command(aliases=['8ball'])
async def vision(ctx, *, question):
    responses = ['Assim é.', 'Está me ameaçando?', 'É certo.', 'Acho que devemos buscar mais informações.', 'Isso não está correto.', 'Você está errado.', '[Não, não, NÃO!!]']
    await ctx.send(f'{random.choice(responses)}')

@vision.error
async def clear_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send('Queria me perguntar algo, Jedi?')

client.run('NzUxMDg3NjY1OTUyMDYzNTgw.X1D-5g.mFT9Vzes5CvYn94CjX_VoMIMY98')
