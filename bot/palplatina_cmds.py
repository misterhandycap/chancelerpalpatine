from datetime import datetime
import discord
from bot.models.user import User
from discord.ext import commands

class PalplatinaCmds(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command()
    async def daily(self, ctx):
        user = await User.get(ctx.message.author.id)
        if not user:
            user = User()
            user.id = ctx.message.author.id
            user.name = ctx.message.author.name
            user.currency = 0
            user.daily_last_collected_at = None



        if user.daily_last_collected_at and (datetime.utcnow() - user.daily_last_collected_at).days < 1:
            
            palplatinasrejeitou = discord.Embed(
                title='Daily!',
                description = f'Você já pegou seu daily hoje. Ambição leva ao lado sombrio da força, gosto disso.',
                colour = discord.Color.greyple(),
                timestamp = ctx.message.created_at
            )
            palplatinasrejeitou.set_thumbnail(url='https://cdn.discordapp.com/attachments/307920220406808576/800525198687731742/palplatina.png')    

            await ctx.send(embed=palplatinasrejeitou)
        else:
            user.daily_last_collected_at = datetime.utcnow()
            user.currency += 300
            palplatinasrecebeu = discord.Embed(
                title = 'Daily!',
                description = f'Você recebeu 300 palplatinas, faça bom uso',
                colour = discord.Color.greyple(),
                timestamp = ctx.message.created_at
            )
            palplatinasrecebeu.set_thumbnail(url='https://cdn.discordapp.com/attachments/307920220406808576/800525198687731742/palplatina.png')
            await ctx.send(embed=palplatinasrecebeu)

        await User.save(user)

    @commands.command(aliases=['conta', 'atm', 'palplatina'])
    async def banco(self, ctx):
        user = await User.get(ctx.message.author.id)
        
        moedas = discord.Embed(
            title='Daily!',
            description=f'{ctx.author.mention} possui {user.currency} palplatinas.',
            colour=discord.Color.greyple(),
            timestamp=ctx.message.created_at
        )
        moedas.set_thumbnail(
            url='https://cdn.discordapp.com/attachments/307920220406808576/800525198687731742/palplatina.png')
        await ctx.send(embed=moedas)
