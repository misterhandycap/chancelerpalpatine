import inspect
import json
import logging
import os
import random
import time

import discord
from discord.ext import commands

from bot.aurebesh import text_to_aurebesh_img
from bot.meme import meme_saimaluco_image, random_cat
from bot.social.profile import Profile
from bot.utils import paginate, PaginatedEmbedManager


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
        logging.info('É bom te ver, mestre Jedi.')

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        try:
            raise error
        except (commands.UserNotFound, commands.MemberNotFound):
            await ctx.reply(
                content='Mestre quem?',
                mention_author=False
            )
        except commands.BadArgument:
            await ctx.reply(
                content=('Parâmetro inválido. '
                'Consulte a descrição do comando abaixo para informações sobre sua correta utilização:'),
                embed=self._create_cmd_help_embed(ctx.command),
                mention_author=False
            )
        except commands.CommandNotFound:
            await ctx.reply(
                content='Esta ordem não existe, agora se me der licença...',
                mention_author=False
            )
        except commands.MissingRequiredArgument:
            await ctx.reply(
                content=f"Esse comando requer um argumento (`{error.param.name}`) que não foi passado. "\
                "Consulte a descrição do comando abaixo para informações sobre sua correta utilização:",
                embed=self._create_cmd_help_embed(ctx.command),
                mention_author=False
            )
        except commands.MissingPermissions:
            await ctx.reply(
                "Você não tem as seguintes permissões necessárias para rodar esse comando: "
                f"`{'`, `'.join(error.missing_perms)}`",
                mention_author=False
            )
        except:
            logging.warning(f'{error.__class__}: {error}')
            await ctx.message.add_reaction('⚠️')

    @commands.command(aliases=['ajuda'])
    async def help(self, ctx, page_or_cmd='1'):
        """
        Exibe essa mensagem.
        Passe um comando para obter mais informações sobre ele
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
            help_embed = await self._create_paginated_help_embed(page_number)
            await self.help_cmd_manager.send_embed(help_embed, page_number, ctx)
        else:
            try:
                cmd = [x for x in bot_commands if cmd_name in [x.name] + x.aliases][0]
            except IndexError:
                return await ctx.send(f"Comando não encontrado. Veja todos os comandos disponíveis com `{bot_prefix}ajuda`")
            help_embed = self._create_cmd_help_embed(cmd)
            await ctx.send(embed=help_embed)

    async def _create_paginated_help_embed(self, page_number):
        max_itens_per_page = 9
        bot_prefix = os.environ.get("BOT_PREFIX", 'cp!')
        bot_commands = sorted(self.client.commands, key=lambda x: x.name)
        
        paginated_commands, last_page = paginate(bot_commands, page_number, max_itens_per_page)
        help_embed = discord.Embed(
            title='Ajuda',
            description=f'Comandos ({min(max(page_number, 1), last_page)}/{last_page}):',
            colour=discord.Color.blurple()
        )
        for cmd in paginated_commands:
            help_embed.add_field(
                name=f'{bot_prefix}{cmd.name}',
                value=cmd.short_doc or 'Sem descrição disponível'
            )
        self.help_cmd_manager.last_page = last_page

        return help_embed

    def _create_cmd_help_embed(self, cmd):
        help_embed = discord.Embed(
            title=f'Ajuda - {cmd.name}',
            description=cmd.help or 'Sem descrição disponível',
            colour=discord.Color.blurple()
        )
        help_embed.add_field(
            name='Nomes alternativos', value='\n'.join(cmd.aliases) or 'Nenhum')
        help_embed.add_field(name='Parâmetros', value=cmd.signature or 'Nenhum')
        help_embed.add_field(
            name='Categoria',
            value=cmd.cog.description if cmd.cog else 'Nenhuma'
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
            return await ctx.send("Não consegui encontrar um gato 😢")
        embed = discord.Embed(title="Gato")
        embed.set_image(url=image_url)
        await ctx.send(embed=embed)

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
            return await ctx.send("Opção inválida")

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
        image = await self.profile_bot.get_user_profile(selected_user.id, user_avatar)
        if not image:
            return await ctx.send('Quem é você?')
        await ctx.send(file=discord.File(image, 'perfil.png'))
