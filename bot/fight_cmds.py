import discord

from bot import fight_bot, client

emoji_answers = {
    'atacar': '⚔',
    'defender': '🛡',
    'abandonar': '🚫'
}

@client.command(aliases=['luta'])
async def fight(ctx, user2: discord.User):
    await ctx.trigger_typing()
    await ctx.send('Batalha iniciada, que o vencedor me sirva bem.')

@client.event
async def on_reaction_add(reaction, user):

