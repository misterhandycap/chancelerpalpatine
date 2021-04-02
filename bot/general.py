import inspect
import json
import logging
import os
import random
import time

import discord
from discord.ext import commands

from bot.across_the_stars.vote import Vote
from bot.aurebesh import text_to_aurebesh_img
from bot.meme import meme_saimaluco_image, random_cat
from bot.servers import cache
from bot.social.profile import Profile
from bot.utils import current_bot_version, get_server_lang, i, paginate, PaginatedEmbedManager


class GeneralCog(commands.Cog):
    """
    Miscelânea
    """

    def __init__(self, client):
        self.client = client
        self.help_cmd_manager = PaginatedEmbedManager(client, self._create_paginated_help_embed)
        self.profile_bot = Profile()

    @commands.Cog.listener()
    async def on_ready(self):
        await self.client.change_presence(
            status=discord.Status.online,
            activity=discord.Game(f'Planejando uma ordem surpresa')
        )
        await cache.load_configs()
        cache.all_servers = self.client.guilds
        logging.info('Bot is ready')

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        try:
            raise error
        except (commands.UserNotFound, commands.MemberNotFound):
            await ctx.reply(
                content=i(ctx, 'Master who?'),
                mention_author=False
            )
        except commands.BadArgument:
            await ctx.reply(
                content=(i(ctx, 'Invalid parameter. ') +
                i(ctx, 'Take a look at the command\'s documentation below for information about its correct usage:')),
                embed=self._create_cmd_help_embed(ctx.command, ctx),
                mention_author=False
            )
        except commands.CommandNotFound:
            await ctx.reply(
                content='Esta ordem não existe, agora se me der licença...',
                mention_author=False
            )
        except commands.MissingRequiredArgument:
            await ctx.reply(
                content=i(ctx, "This command requires an argument (`{command_name}`) that has not been provided. ")
                .format(command_name=error.param.name)+
                i(ctx, 'Take a look at the command\'s documentation below for information about its correct usage:'),
                embed=self._create_cmd_help_embed(ctx.command, ctx),
                mention_author=False
            )
        except commands.MissingPermissions:
            await ctx.reply(
                i(ctx, "You do not have the required permissions to run this command: ") +
                f"`{'`, `'.join(error.missing_perms)}`",
                mention_author=False
            )
        except:
            logging.warning(f'{error.__class__}: {error}')
            await ctx.message.add_reaction('⚠️')

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.content.strip() == f'<@!{self.client.user.id}>':
            await message.reply(
                content='Olá, segue abaixo algumas informações sobre mim 😊',
                embed=await self._create_info_embed(message),
                mention_author=False
            )

    @commands.command(aliases=['ajuda'])
    async def help(self, ctx, page_or_cmd='1'):
        """
        Exibe essa mensagem

        Passe um comando para obter mais informações sobre ele.

        Parâmetros de comandos entre sinais de maior e menor (`<parametro>`) sinalizam \
            parâmetros obrigatórios. Já parâmetros entre colchetes (`[parametro]`) \
            sinalizam parâmetros opcionais. Valores padrões são sinalizados com um \
            sinal de igual (`[parametro=valor_padrao]`).
        """
        page_number = None
        cmd_name = None
        try:
            page_number = int(page_or_cmd)
        except:
            cmd_name = page_or_cmd

        bot_prefix = os.environ.get("BOT_PREFIX", 'cp!')
        bot_commands = sorted(self.client.commands, key=lambda x: x.name)
        
        if page_number:
            help_embed = await self._create_paginated_help_embed(page_number, ctx)
            await self.help_cmd_manager.send_embed(help_embed, page_number, ctx)
        else:
            try:
                cmd = [x for x in bot_commands if cmd_name in [x.name] + x.aliases][0]
            except IndexError:
                return await ctx.send(f'{i(ctx, "Command not found. Check all available commands with")} `{bot_prefix}ajuda`')
            help_embed = self._create_cmd_help_embed(cmd, ctx)
            await ctx.send(embed=help_embed)

    async def _create_paginated_help_embed(self, page_number, original_message):
        max_itens_per_page = 9
        bot_prefix = os.environ.get("BOT_PREFIX", 'cp!')
        bot_commands = sorted(self.client.commands, key=lambda x: x.name)
        
        paginated_commands, last_page = paginate(bot_commands, page_number, max_itens_per_page)
        help_embed = discord.Embed(
            title=i(original_message, 'Help'),
            description=f'{i(original_message, "Commands")} ({min(max(page_number, 1), last_page)}/{last_page}):',
            colour=discord.Color.blurple()
        )
        for cmd in paginated_commands:
            cmd_short_description = i(original_message, f'cmd_{cmd.name}').split("\n")[0]
            if cmd_short_description == f'cmd_{cmd.name}':
                cmd_short_description = 'No description available'
            
            help_embed.add_field(
                name=f'{bot_prefix}{cmd.name}',
                value=cmd_short_description
            )
        self.help_cmd_manager.last_page = last_page

        return help_embed

    def _create_cmd_help_embed(self, cmd, ctx):
        cmd_description = i(ctx, f'cmd_{cmd.name}')
        if cmd_description == f'cmd_{cmd.name}':
            cmd_description = 'No description available'
        
        help_embed = discord.Embed(
            title=f'{i(ctx, "Help")} - {cmd.name}',
            description=cmd_description,
            colour=discord.Color.blurple()
        )
        help_embed.add_field(
            name=i(ctx, 'Aliases'), value='\n'.join(cmd.aliases) or i(ctx, 'None'))
        help_embed.add_field(name=i(ctx, 'Arguments'), value=cmd.signature or i(ctx, 'None'))
        help_embed.add_field(
            name=i(ctx, 'Category'),
            value=cmd.cog.description if cmd.cog and cmd.cog.description else i(ctx, 'None')
        )
        return help_embed

    @commands.command()
    async def saimaluco(self, ctx, *, text):
        """
        Manda o meme sai maluco com o texto enviado
        """
        image = meme_saimaluco_image(text)
        await ctx.send(file=discord.File(image, 'meme.png'))
    
    @commands.command()
    async def aurebesh(self, ctx, *, text):
        """
        Gera uma imagem com o texto fornecido em Aurebesh
        """
        image = text_to_aurebesh_img(text)
        await ctx.send(file=discord.File(image, 'aurebesh.png'))
    
    @commands.command()
    async def ping(self, ctx):
        """
        Confere se o bot está online e sua velocidade de resposta
        """
        ping = discord.Embed(
            title='Pong...',
            description=f'{round(self.client.latency * 1000)}ms',
            colour=discord.Color.blurple(),
            timestamp=ctx.message.created_at
        )
        await ctx.send(embed=ping)

    @commands.command()
    async def info(self, ctx):
        """
        Mostra informações sobre o bot
        """
        embed = await self._create_info_embed(ctx)
        await ctx.send(embed=embed)

    async def _create_info_embed(self, ctx):
        bot_prefix = self.client.command_prefix
        bot_info = await self.client.application_info()
        bot_owner = bot_info.team.owner

        embed = discord.Embed(
            title=bot_info.name,
            description=bot_info.description,
            colour=discord.Color.blurple(),
            url=os.environ.get("BOT_HOMEPAGE")
        )
        embed.set_thumbnail(url=bot_info.icon_url)
        embed.add_field(name=i(ctx, 'Owner'), value=f'{bot_owner.name}#{bot_owner.discriminator}')
        if current_bot_version:
            embed.add_field(name=i(ctx, 'Current version'), value=current_bot_version)
        embed.add_field(name=i(ctx, 'Prefix'), value=bot_prefix)
        embed.add_field(name=i(ctx, 'Help cmd'), value=f'{bot_prefix}help')
        return embed

    @commands.command(aliases=['limpar', 'clean'])
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int):
        """
        Limpa as últimas mensagens do canal atual
        """
        await ctx.channel.purge(limit=amount+1)

    @commands.command(aliases=['8ball'])
    async def vision(self, ctx, *, question):
        """
        Faça uma pergunta ao Chanceler e ele irá lhe responder
        """
        responses = [
            'Assim é.',
            'Está me ameaçando?',
            'É certo.',
            'Acho que devemos buscar mais informações.',
            'Isso não está correto.',
            'Você está errado(a).',
            'Não, não, NÃO!!', 
            'Acredito que esteja errado(a), Mestre', 
            'Isso necessita de mais análises'
        ]
        await ctx.send(f'{random.choice(responses)}')

    @vision.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send('Queria me perguntar algo, Jedi?')

    @commands.command(aliases=['caracoroa'])
    async def sorte(self, ctx):
        """
        Cara ou coroa
        """
        previsao = ['Cara', 'Coroa']
        await ctx.send(f'{random.choice(previsao)}')

    @commands.command(aliases=['cat'])
    async def gato(self, ctx):
        """
        Mostra uma foto aleatória de gato 🐈
        """
        await ctx.trigger_typing()
        image_url = await random_cat()
        if not image_url:
            return await ctx.send(i(ctx, "Could not find a cat picture 😢"))
        embed = discord.Embed(title="Gato")
        embed.set_image(url=image_url)
        await ctx.send(embed=embed)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def lang(self, ctx, language_code):
        """
        Muda o idioma do bot no servidor atual

        Passe um código válido de idioma. Consulte os códigos válidos nesse link: \
            https://www.gnu.org/software/gettext/manual/html_node/Usual-Language-Codes.html
        """
        await cache.update_config(ctx.guild.id, language=language_code)
        return await ctx.send(i(ctx, 'Language updated to {lang}').format(lang=language_code))

    @commands.command(aliases=['pedrapapeltesoura', 'ppt', 'dino'])
    async def rps(self, ctx, player_choice_str):
        """
        Pedra, papel e tesoura com dinossauros

        Jogadas válidas: `Deus`, `Homem`, `Dinossauro`.

        Regras: Homem ganha de Deus, Dinossauro ganha de Homem, \
            Deus ganha de Dinossauro e Mulher herda a Terra em caso de empate.
        """
        player_choice_str = player_choice_str.title()
        available_options = ['Deus', 'Homem', 'Dinossauro']
        if player_choice_str not in available_options:
            return await ctx.send(i(ctx, "Invalid option"))

        player_choice = available_options.index(player_choice_str)
        bot_choice = random.randint(0,2)
        bot_choice_str = available_options[bot_choice]

        if bot_choice == player_choice:
            result = "Mulher herda a Terra"
        else:
            winner_choice = max(bot_choice, player_choice) if abs(bot_choice - player_choice) == 1 else min(bot_choice, player_choice)
            action_txt = ' destrói '
            if winner_choice == player_choice:
                who = 'Você ganhou o jogo'
                winner, loser = player_choice_str, bot_choice_str
            else:
                who = 'Você perdeu o jogo'
                winner, loser = bot_choice_str, player_choice_str
            if winner == 'Dinossauro':
                action_txt = ' come o '
            result = f'{winner}{action_txt}{loser}\n{who}'

        resp_message = f"O bot escolheu: {bot_choice_str}\n{result}"
        await ctx.send(resp_message)

    @commands.command()
    async def plagueis(self, ctx):
        """
        Conta a tregédia de Darth Plagueis
        """
        plagueis = discord.Embed(
            title='Já ouviu a tragédia de Darth Plagueis, o sábio?...',
            description='Eu achei que não. \nNão é uma história que um Jedi lhe contaria.\nÉ uma lenda Sith. \nDarth Plagueis era um Lorde Sombrio de Sith, tão poderoso e tão sábio que conseguia utilizar a Força para influenciar os midiclorians para criar vida. \nEle tinha tantos conhecimento do lado sombrio que podia até impedir que aqueles que lhe eram próximos morressem. \nAcontece que o lado sombrio é o caminho para muitas habilidades que muitos consideram serem... não naturais. \nEle se tornou tão poderoso; que a única coisa que ele tinha medo era, perder seu poder, o que acabou, é claro, ele perdeu. \nInfelizmente, ele ensinou a seu aprendiz tudo o que sabia; então, seu o seu aprendiz o matou enquanto dormia. \nÉ irônico. \nEle poderia salvar outros da morte, mas não podia a salvar a si mesmo.',
            colour=discord.Color.blurple(),
            timestamp=ctx.message.created_at
        )
        await ctx.send(embed=plagueis)

    @commands.command(aliases=['google', 'buscar', 'search'])
    async def busca(self, ctx, *, query):
        """
        Faz uma busca pelo buscador definido

        Passe o nome do buscador como primeiro argumento e sua busca na sequência. \
            Se nenhum buscador for definido, o Google será utilizado.

        Buscadores disponíveis: Google, Star Wars Wiki em Português, Wookieepedia, \
            Avatar Wiki 🇧🇷
        
        Exemplo com buscador definido: `busca sww Sheev Palpatine`
        Exemplo sem buscador definido: `busca Sheev Palpatine`
        """
        providers = {
            'sww':'https://starwars.fandom.com/pt/wiki/',
            'starwarswiki':'https://starwars.fandom.com/pt/wiki/',
            'wookie':'https://starwars.fandom.com/wiki/',
            'google':'https://www.google.com/search?q=',
            'aw':'https://avatar.fandom.com/pt-br/wiki/',
            'avatar':'https://avatar.fandom.com/pt-br/wiki/',
        }

        search_provider = query.split(" ")[0]
        if search_provider.lower() in providers:
            search_engine = providers[search_provider.lower()]
            actual_query = query[len(search_provider)+1:]
        else:
            search_engine = providers["google"]
            actual_query = query
        
        await ctx.send(f'{search_engine}{actual_query.replace(" ", "_")}')

    @commands.command(aliases=['perfil'])
    async def profile(self, ctx, user: discord.User=None):
        """
        Exibe o seu perfil ou de um usuário informado
        """
        await ctx.trigger_typing()
        selected_user = user if user else ctx.message.author
        user_avatar = await selected_user.avatar_url_as(
            size=128, static_format='png').read()
        image = await self.profile_bot.get_user_profile(
            selected_user.id, user_avatar, get_server_lang(ctx.message.guild.id))
        if not image:
            return await ctx.send(i(ctx, 'Who are you?'))
        await ctx.send(file=discord.File(image, 'perfil.png'))

    @commands.command(aliases=['cor_perfil', 'perfil_cor'])
    async def profile_frame_color(self, ctx, color):
        try:
            await self.profile_bot.set_user_profile_frame_color(ctx.message.author.id, color)
            return await ctx.send(i(ctx, 'Profile color updated to {color}').format(color=color))
        except ValueError:
            return await ctx.send(i(ctx, 'Invalid color'))

    @commands.command(aliases=['votar', 'vote', 'poll'])
    async def voto(self, ctx, *, args):
        """
        Cria uma votação para as demais pessoas participarem

        A pergunta e as opções devem ser separadas por `;`. Você pode criar votações \
            com até dez opções.

        Exemplo: `voto Quem é o melhor lorde Sith?;Darth Sidious;Darth Vader;Darth Tyranus`
        """
        emoji_answers_vote = [
            '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟'
        ]
        choices_limit = len(emoji_answers_vote) + 1
        options = args.split(';')
        question = options[0]
        choices = options[1:choices_limit]
        
        embed = discord.Embed(
            title=i(ctx, 'Vote'),
            description=i(ctx, 'Vote on your colleague\'s proposition!'),
            colour=discord.Color.red()
        )
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/676574583083499532/752314249610657932/1280px-Flag_of_the_Galactic_Republic.png")
        embed.add_field(  
            name=i(ctx, 'Democracy!'),
            value=i(ctx, 'I love democracy! {username} has summoned a vote! The proposition is **{question}**, and its options are:\n{options}').format(
                username=ctx.message.author.mention,
                question=question,
                options=''.join([f'\n{emoji} - {choice}' for emoji, choice in zip(emoji_answers_vote, choices)])
            )
        )

        response_msg = await ctx.send(embed=embed)
        for emoji in emoji_answers_vote[:len(choices)]:
            await response_msg.add_reaction(emoji)
