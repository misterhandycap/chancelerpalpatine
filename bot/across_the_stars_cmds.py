from bot.across_the_stars.planets import Planets
import discord
from discord.ext import commands


class AcrossTheStarsCmds(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.planets = Planets()

    @commands.command(aliases=['planets'])
    async def planetas(self, ctx, *, args):
        planets = await self.planets.list_of_planets(region=args)
        
    discord_file = discord.File(
            os.path.join('bot', 'images', 'arnaldo-o-hutt.gif'), 'hutt.gif')
        await self.shop_paginated_embed_manager.send_embed(
            await self._build_shop_embed(page_number), page_number,
            ctx, discord_file
        )

        embed = discord.Embed(
            title='Empório do Arnaldo',
            description='Se torne senador em nome de um planeta.',
            colour=discord.Color.green()
        )
        embed.set_thumbnail(url="attachment://hutt.gif")
        self.shop_paginated_embed_manager.last_page = last_page
        for planet in planets:
            embed.add_field(
                name=profile_item.name,
                value=f'Preço: {profile_item.price}\nTipo: {profile_item.type.name.capitalize()}'

        await ctx.reply(embed=embed
        mention_author=False)
