import discord

from bot import akinator_bot, client

@client.command(aliases=['an'])
async def akinator_novo(ctx):
    game, question = await akinator_bot.new_game(ctx.author)
    await ctx.send("Jogo iniciado. Responda com `cp!akinator_responder RESPOSTA`")
    await ctx.send(f'{ctx.author.name}: {question}')

@client.command(aliases=['ar'])
async def akinator_responder(ctx, answer):
    game = akinator_bot.get_user_game(ctx.author)
    if not game:
        return await ctx.send("Você não está jogando com o Akinator. Para fazê-lo, `cp!akinator_novo`.")
    result = await akinator_bot.answer_question(game, answer)
    if isinstance(result, str):
        await ctx.send(f'{ctx.author.name}: {result}')
    else:
        await ctx.send(f"Você pensou em {result.get('name')}, {result.get('description')}")
