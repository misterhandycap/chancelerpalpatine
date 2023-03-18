import logging
import os
import random
from io import BytesIO
from typing import Literal

import discord
from discord import app_commands
from discord.ext import commands

from bot.aurebesh import text_to_aurebesh_img
from bot.meme import meme_saimaluco_image, random_cat
from bot.misc.scheduler import Scheduler
from bot.servers import cache
from bot.social.profile import Profile
from bot.utils import (PaginatedEmbedManager, current_bot_version,
                       get_server_lang, i, paginate, server_language_to_tz)


class GeneralCmds(app_commands.Group):
    """
    Miscelânea
    """

    def __init__(self, client):
        self.client = client
        self.client.add_listener(self.on_ready)
        self.client.add_listener(self.on_message)
        self.help_cmd_manager = PaginatedEmbedManager(self._create_paginated_help_embed)
        self.profile_bot = Profile()
        self.scheduler_bot = Scheduler()
        self.scheduler_bot.register_function('send_msg', self._send_msg)
        self.scheduler_bot.start()
        super().__init__(name='general')

    async def on_ready(self):
        await self.client.change_presence(
            status=discord.Status.online,
            activity=discord.Game(f'Planejando uma ordem surpresa')
        )
        await cache.load_configs()
        cache.all_servers = self.client.guilds
        logging.info('Bot is ready')

    async def on_error(self, interaction: discord.Interaction, error):
        try:
            raise error
        except (commands.UserNotFound, commands.MemberNotFound):
            await interaction.response.send_message(
                content=i(interaction, 'Master who?')
            )
        except commands.BadArgument:
            await interaction.response.send_message(
                content=(i(interaction, 'Invalid parameter. ') +
                i(interaction, 'Take a look at the command\'s documentation below for information about its correct usage:')),
                embed=self._create_cmd_help_embed(interaction.command, interaction)
            )
        except commands.CommandNotFound:
            await interaction.response.send_message(
                content='Esta ordem não existe, agora se me der licença...'
            )
        except commands.MissingRequiredArgument:
            await interaction.response.send_message(
                content=i(interaction, "This command requires an argument (`{command_name}`) that has not been provided. ")
                .format(command_name=error.param.name)+
                i(interaction, 'Take a look at the command\'s documentation below for information about its correct usage:'),
                embed=self._create_cmd_help_embed(interaction.command, interaction)
            )
        except app_commands.errors.MissingPermissions:
            await interaction.response.send_message(
                i(interaction, "You do not have the required permissions to run this command: ") +
                f"`{'`, `'.join(error.missing_permissions)}`"
            )
        except commands.PrivateMessageOnly:
            await interaction.response.send_message(
                i(interaction, "Command only available through DM")
            )
        except:
            logging.warning(f'{error.__class__}: {error}')
            logging.exception(error)

    async def on_message(self, message):
        if message.content.strip() == f'<@!{self.client.user.id}>':
            await message.reply(
                content='Olá, segue abaixo algumas informações sobre mim 😊',
                embed=await self._create_info_embed(message)
            )

    @commands.command(aliases=['ajuda'])
    async def help(self, interaction: discord.Interaction, page_or_cmd='1'):
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
            help_embed = await self._create_paginated_help_embed(page_number, interaction)
            await self.help_cmd_manager.send_embed(help_embed, page_number, interaction)
        else:
            try:
                cmd = [x for x in bot_commands if cmd_name in [x.name] + x.aliases][0]
            except IndexError:
                return await interaction.send(f'{i(interaction, "Command not found. Check all available commands with")} `{bot_prefix}ajuda`')
            help_embed = self._create_cmd_help_embed(cmd, interaction)
            await interaction.send(embed=help_embed)

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

    def _create_cmd_help_embed(self, cmd, interaction):
        cmd_description = i(interaction, f'cmd_{cmd.name}')
        if cmd_description == f'cmd_{cmd.name}':
            cmd_description = 'No description available'
        
        help_embed = discord.Embed(
            title=f'{i(interaction, "Help")} - {cmd.name}',
            description=cmd_description,
            colour=discord.Color.blurple()
        )
        help_embed.add_field(
            name=i(interaction, 'Aliases'), value='\n'.join(cmd.aliases) or i(interaction, 'None'))
        help_embed.add_field(name=i(interaction, 'Arguments'), value=cmd.signature or i(interaction, 'None'))
        help_embed.add_field(
            name=i(interaction, 'Category'),
            value=cmd.cog.description if cmd.cog and cmd.cog.description else i(interaction, 'None')
        )
        return help_embed

    @app_commands.command(
        name="saimaluco",
        description="Manda o meme sai maluco com o texto enviado"
    )
    @app_commands.describe(text='Texto')
    async def saimaluco(self, interaction: discord.Interaction, text: str):
        """
        Manda o meme sai maluco com o texto enviado
        """
        await interaction.response.defer()
        image = meme_saimaluco_image(text)
        await interaction.followup.send(file=discord.File(image, 'meme.png'))
    
    @app_commands.command(
        name="aurebesh",
        description="Gera uma imagem com o texto fornecido em Aurebesh"
    )
    @app_commands.describe(text='Texto')
    async def aurebesh(self, interaction: discord.Interaction, text: str):
        """
        Gera uma imagem com o texto fornecido em Aurebesh
        """
        await interaction.response.defer()
        image = text_to_aurebesh_img(text)
        await interaction.followup.send(file=discord.File(image, 'aurebesh.png'))
    
    @app_commands.command(
        name="ping",
        description="Confere se o bot está online e sua velocidade de resposta"
    )
    async def ping(self, interaction: discord.Interaction):
        """
        Confere se o bot está online e sua velocidade de resposta
        """
        ping = discord.Embed(
            title='Pong...',
            description=f'{round(self.client.latency * 1000)}ms',
            colour=discord.Color.blurple()
        )
        await interaction.response.send_message(embed=ping)

    @app_commands.command(
        name="info",
        description="Mostra informações sobre o bot"
    )
    async def info(self, interaction: discord.Interaction):
        """
        Mostra informações sobre o bot
        """
        embed = await self._create_info_embed(interaction)
        await interaction.response.send_message(embed=embed)

    async def _create_info_embed(self, interaction: discord.Interaction):
        bot_prefix = self.client.command_prefix
        bot_info = await self.client.application_info()
        bot_owner = bot_info.team.owner

        embed = discord.Embed(
            title=bot_info.name,
            description=bot_info.description,
            colour=discord.Color.blurple(),
            url=os.environ.get("BOT_HOMEPAGE")
        )
        embed.set_thumbnail(url=bot_info.icon.url)
        embed.add_field(name=i(interaction, 'Owner'), value=f'{bot_owner.name}#{bot_owner.discriminator}')
        if current_bot_version:
            embed.add_field(name=i(interaction, 'Current version'), value=current_bot_version)
        embed.add_field(name=i(interaction, 'Prefix'), value=bot_prefix)
        embed.add_field(name=i(interaction, 'Help cmd'), value=f'{bot_prefix}help')
        return embed

    @app_commands.command(
        name='lembrete',
        description='Crie um lembre'
    )
    @app_commands.describe(datetime='Data para lembrete', text='Mensagem do lembrete')
    async def remind(self, interaction: discord.Interaction, datetime: str, text: str):
        server_timezone = server_language_to_tz.get(get_server_lang(interaction.guild_id), 'UTC')
        schedule_datetime = self.scheduler_bot.parse_schedule_time(datetime, server_timezone)
        if schedule_datetime is None:
            return await interaction.response.send_message(i(interaction, "Invalid datetime format. Examples of valid formats: {}").format(
                ", ".join(["`5 d`", "`15 s`", "`2020/12/31 12:59`", "`8 h`", "`60 min`"])
            ))
        
        self.scheduler_bot.add_job(schedule_datetime, 'send_msg', (interaction.user.id, interaction.channel_id, text))
        await interaction.response.send_message(i(interaction, 'Message "{text}" scheduled for {datetime}').format(
            text=text,
            datetime=schedule_datetime.strftime("%d/%m/%Y %H:%M:%S %Z")
        ))

    async def _send_msg(self, user_id, channel_id, text):
        channel = await self.client.fetch_channel(channel_id)
        user = await self.client.fetch_user(user_id)
        await channel.send(f'{user.mention}: {text}')

    @app_commands.command(
        name="clear",
        description="Limpa as últimas mensagens do canal atual",
    )
    @app_commands.describe(amount='Número de mensagens a excluir')
    @app_commands.checks.has_permissions(manage_messages=True)
    async def clear(self, interaction: discord.Interaction, amount: int):
        """
        Limpa as últimas mensagens do canal atual
        """
        await interaction.channel.purge(limit=amount)
        return await interaction.response.send_message('Done')

    @app_commands.command(
        name="vision",
        description="Faça uma pergunta ao Chanceler e ele irá lhe responder"
    )
    @app_commands.describe(question='Pergunta')
    async def vision(self, interaction: discord.Interaction, question: str):
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
        await interaction.response.send_message(f'{random.choice(responses)}')

    @app_commands.command(
        name="sorte",
        description="Cara ou coroa"
    )
    async def sorte(self, interaction: discord.Interaction):
        """
        Cara ou coroa
        """
        previsao = ['Cara', 'Coroa']
        await interaction.response.send_message(f'{random.choice(previsao)}')

    @app_commands.command(
        name="gato",
        description="Mostra uma foto aleatória de gato 🐈"
    )
    async def random_cat(self, interaction: discord.Interaction):
        """
        Mostra uma foto aleatória de gato 🐈
        """
        await interaction.response.defer()
        image_url = await random_cat()
        if not image_url:
            return await interaction.followup.send(i(interaction, "Could not find a cat picture 😢"))
        embed = discord.Embed(title="Gato")
        embed.set_image(url=image_url)
        await interaction.followup.send(embed=embed)

    @app_commands.command(
        name="lang",
        description="Muda o idioma do bot no servidor atual",
    )
    @app_commands.describe(language_code='Código válido de idioma')
    @app_commands.checks.has_permissions(administrator=True)
    async def lang(self, interaction: discord.Interaction, language_code: str):
        """
        Muda o idioma do bot no servidor atual

        Passe um código válido de idioma. Consulte os códigos válidos nesse link: \
            https://www.gnu.org/software/gettext/manual/html_node/Usual-Language-Codes.html
        """
        await cache.update_config(interaction.guild.id, language=language_code)
        return await interaction.response.send_message(i(interaction, 'Language updated to {lang}').format(lang=language_code))

    @app_commands.command(
        name="rps",
        description="Pedra, papel e tesoura com dinossauros"
    )
    @app_commands.describe(play='Jogada')
    async def rps(self, interaction: discord.Interaction, play: Literal['Deus', 'Homem', 'Dinossauro']):
        """
        Pedra, papel e tesoura com dinossauros

        Jogadas válidas: `Deus`, `Homem`, `Dinossauro`.

        Regras: Homem ganha de Deus, Dinossauro ganha de Homem, \
            Deus ganha de Dinossauro e Mulher herda a Terra em caso de empate.
        """
        play = play.title()
        available_options = ['Deus', 'Homem', 'Dinossauro']
        if play not in available_options:
            return await interaction.response.send_message(i(interaction, "Invalid option"))

        player_choice = available_options.index(play)
        bot_choice = random.randint(0,2)
        bot_choice_str = available_options[bot_choice]

        if bot_choice == player_choice:
            result = "Mulher herda a Terra"
        else:
            winner_choice = max(bot_choice, player_choice) if abs(bot_choice - player_choice) == 1 else min(bot_choice, player_choice)
            action_txt = ' destrói '
            if winner_choice == player_choice:
                who = 'Você ganhou o jogo'
                winner, loser = play, bot_choice_str
            else:
                who = 'Você perdeu o jogo'
                winner, loser = bot_choice_str, play
            if winner == 'Dinossauro':
                action_txt = ' come o '
            result = f'{winner}{action_txt}{loser}\n{who}'

        resp_message = f"O bot escolheu: {bot_choice_str}\n{result}"
        await interaction.response.send_message(resp_message)

    @app_commands.command(
        name="plagueis",
        description="Conta a tregédia de Darth Plagueis"
    )
    async def plagueis(self, interaction: discord.Interaction):
        """
        Conta a tregédia de Darth Plagueis
        """
        plagueis = discord.Embed(
            title='Já ouviu a tragédia de Darth Plagueis, o sábio?...',
            description='Eu achei que não. \nNão é uma história que um Jedi lhe contaria.\nÉ uma lenda Sith. \nDarth Plagueis era um Lorde Sombrio de Sith, tão poderoso e tão sábio que conseguia utilizar a Força para influenciar os midiclorians para criar vida. \nEle tinha tantos conhecimento do lado sombrio que podia até impedir que aqueles que lhe eram próximos morressem. \nAcontece que o lado sombrio é o caminho para muitas habilidades que muitos consideram serem... não naturais. \nEle se tornou tão poderoso; que a única coisa que ele tinha medo era, perder seu poder, o que acabou, é claro, ele perdeu. \nInfelizmente, ele ensinou a seu aprendiz tudo o que sabia; então, seu o seu aprendiz o matou enquanto dormia. \nÉ irônico. \nEle poderia salvar outros da morte, mas não podia a salvar a si mesmo.',
            colour=discord.Color.blurple()
        )
        await interaction.response.send_message(embed=plagueis)

    @app_commands.command(
        name="busca",
        description="Faz uma busca pelo buscador definido"
    )
    @app_commands.describe(query='Busca', provider='Buscador')
    async def get_search_url(self, interaction: discord.Interaction, query: str,
                             provider: Literal['google', 'sww', 'wookiee', 'aw']='google'):
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

        search_engine = providers[provider]
        actual_query = query
        
        await interaction.response.send_message(f'{search_engine}{actual_query.replace(" ", "_")}')

    @app_commands.command(
        name="avatar",
        description="Exibe o avatar de um usuário"
    )
    @app_commands.describe(user='Usuáriuo para exibir o avatar')
    async def avatar(self, interaction: discord.Interaction, user: discord.User=None):
        await interaction.response.defer()
        selected_user = user or interaction.user
        await interaction.followup.send(file=discord.File(
            BytesIO(await selected_user.display_avatar.read()),
            'avatar.png'
        ))
    
    @app_commands.command(
        name="perfil",
        description="Exibe o seu perfil ou de um usuário informado"
    )
    @app_commands.describe(user='Usuário para exibir o perfil')
    async def profile(self, interaction: discord.Interaction, user: discord.User=None):
        """
        Exibe o seu perfil ou de um usuário informado
        """
        await interaction.response.defer()
        selected_user = user or interaction.user
        user_avatar = await selected_user.avatar.read()
        image = await self.profile_bot.get_user_profile(
            selected_user.id, user_avatar, get_server_lang(interaction.guild_id))
        if not image:
            return await interaction.followup.send(i(interaction, 'Who are you?'))
        await interaction.followup.send(file=discord.File(image, 'perfil.png'))

    @app_commands.command(
        name="profile_frame_color",
        description="Atualiza a cor das bordas de seu perfil"
    )
    @app_commands.describe(color='Cor que deseja em valor hex')
    async def profile_frame_color(self, interaction: discord.Interaction, color: str):
        try:
            await self.profile_bot.set_user_profile_frame_color(interaction.user.id, color)
            return await interaction.response.send_message(i(interaction, 'Profile color updated to {color}').format(color=color))
        except ValueError:
            return await interaction.response.send_message(i(interaction, 'Invalid color'))

    @app_commands.command(
        name="voto",
        description="Cria uma votação para as demais pessoas participarem"
    )
    @app_commands.describe(args='A pergunta e as opções devem ser separadas por `;`')
    async def poll(self, interaction: discord.Interaction, args: str):
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
            title=i(interaction, 'Vote'),
            description=i(interaction, 'Vote on your colleague\'s proposition!'),
            colour=discord.Color.red()
        )
        embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/676574583083499532/752314249610657932/1280px-Flag_of_the_Galactic_Republic.png")
        embed.add_field(  
            name=i(interaction, 'Democracy!'),
            value=i(interaction, 'I love democracy! {username} has summoned a vote! The proposition is **{question}**, and its options are:\n{options}').format(
                username=interaction.user.mention,
                question=question,
                options=''.join([f'\n{emoji} - {choice}' for emoji, choice in zip(emoji_answers_vote, choices)])
            )
        )

        await interaction.response.send_message(embed=embed)
        response_msg = await interaction.original_response()
        for emoji in emoji_answers_vote[:len(choices)]:
            await response_msg.add_reaction(emoji)
