import discord
import random
import json
import os
from discord.ext import commands
from client import client

@client.check
async def globally_block_dms(ctx):
    return ctx.guild is not None

@client.event
async def on_ready():
    await client.change_presence(status=discord.Status.online, activity=discord.Game(f'Planejando uma ordem surpresa'))
    print('É bom te ver, mestre Jedi.')

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

#os.system('python level.py')
