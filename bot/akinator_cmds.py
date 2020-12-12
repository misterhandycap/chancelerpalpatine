import discord

from bot import akinator_bot, client

emoji_answers = {
    'y': '✅',
    'p': '🇵',
    'idk': '🤷',
    'pn': '🇺',
    'n': '🚫'
}

@client.command(aliases=['an'])
async def akinator_novo(ctx):
    """
    Novo jogo com Akinator
    """
    await ctx.trigger_typing()
    game, question = await akinator_bot.new_game(ctx.author)
    await ctx.send("Jogo iniciado. Responda reagindo às perguntas do bot.")
    await send_embed(question, ctx.author, ctx)

@client.event
async def on_reaction_add(reaction, user):
    game = akinator_bot.get_user_game(user)
    if not game or not reaction.message.embeds:
        return
    embed = reaction.message.embeds[0]
    if 'Akinator' not in embed.title:
        return

    emoji = str(reaction)
    if emoji not in emoji_answers.values():
        return
    
    await reaction.message.channel.trigger_typing()
    answer = [k for k, v in emoji_answers.items() if v == emoji][0]
    result = await akinator_bot.answer_question(game, answer)
    if isinstance(result, str):
        await send_embed(result, user, reaction.message.channel)
    else:
        embed = discord.Embed(
            title=f'{user.name} pensou em {result.get("name")}',
            description=result.get('description'),
            colour=discord.Color.blurple()
        )
        embed.set_thumbnail(url=result.get('absolute_picture_path'))
        await reaction.message.channel.send(embed=embed)

async def send_embed(result, user, channel):
    embed = discord.Embed(
        title=f'Akinator: {user.name}',
        description=result,
        colour=discord.Color.blurple()
    )
    message = await channel.send(embed=embed)
    for emoji in emoji_answers.values():
        await message.add_reaction(emoji)
