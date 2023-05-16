import logging
import os
import re
from typing import Dict, List

from aiohttp import ClientSession, ClientResponseError
from pywikibot import APISite, config, Page, Site
from pywikibot.login import ClientLoginManager, BotPassword
from mwparserfromhell import parse as mwparse
from mwparserfromhell.wikicode import Wikicode
from mwparserfromhell.nodes.tag import Tag

from bot.sww.sww_family import StarWarsWikiFamily
from bot.utils import run_blocking_io_task


class TimelineTranslator():
    WOOKIEE_TIMELINE_URL = "http://starwars.wikia.com/wiki/Timeline_of_canon_media?action=raw"
    
    def __init__(self, auto_close_session: bool=False) -> None:
        self.auto_close_session = auto_close_session
        self.client_session: ClientSession = None
        self.page: Page = None
        self._site: APISite = None
        self._original_content: str = None
        self._current_content: str = None
        self._translated_refs: Dict[str, str] = {}
        self._current_revision: int = None
        config.put_throttle = 1
    
    @run_blocking_io_task
    def login(self) -> None:
        logging.getLogger('pywiki').disabled = True
        bot_password = BotPassword(
            os.environ.get("SWW_BOT_USERNAME"), os.environ.get('SWW_BOT_PASSWORD'))
        login_manager = ClientLoginManager(site=self._site, user=self._site.username())
        login_manager.password = bot_password.password
        login_manager.login_name = bot_password.login_name(login_manager.username)
        login_manager.login()
        logging.getLogger('pywiki').disabled = False
        self._site._username = login_manager.username
        del self._site.userinfo
        self._site.userinfo
    
    async def get_wookiee_page(self) -> str:
        if not self.client_session:
            self.client_session = ClientSession(raise_for_status=True)
            
        try:
            async with self.client_session.get(self.WOOKIEE_TIMELINE_URL) as response:
                self._original_content = await response.text()
                return self._original_content
        except ClientResponseError as e:
            logging.warning(e, exc_info=True)
            raise Exception("Error fetching content")
        finally:
            if self.auto_close_session:
                await self.client_session.close()
                
    @run_blocking_io_task
    def get_timeline_page(self) -> Page:
        self._site = APISite(fam=StarWarsWikiFamily(), code='pt', user=os.environ.get("SWW_BOT_USERNAME"))
        self.page = Page(self._site, u"Linha do tempo de mídia canônica")
        self._current_content = self.page.text
        self._current_revision = self.page.latest_revision_id
        return self.page
                
    def build_new_references(self) -> Dict[str, str]:
        if not self._original_content or not self._current_content:
            raise Exception("Load both Wookieepedia and SWW content first")
        
        original_refs = self._build_reference_dict(self._original_content)
        current_refs = self._build_reference_dict(self._current_content)
        self._translated_refs = current_refs
        
        return {k: v for k, v in original_refs.items() if k not in current_refs}
    
    def add_reference_translation(self, reference_name: str, content: str) -> None:
        self._translated_refs[reference_name] = content
        
    def translate_page(self) -> Page:
        parsed_current_content: Wikicode = mwparse(self._current_content, skip_style_tags=True)
        current_main_table = self._get_tags_from_wikitext(parsed_current_content, 'table')[1]
        parsed_original_content: Wikicode = mwparse(self._original_content, skip_style_tags=True)
        original_main_table = self._get_tags_from_wikitext(parsed_original_content, 'table')[1]
        
        translated_contents = self._apply_translations(str(original_main_table.contents))
        current_main_table.contents = translated_contents
        all_refs = self._get_tags_from_wikitext(current_main_table.contents, 'ref')
        translated_ref_names = {self._apply_translations(k): k for k in self._translated_refs.keys()}
        try:
            for tag in all_refs:
                if tag.contents:
                    tag_name_attr = tag.get('name')
                    tag_original_name = translated_ref_names[str(tag_name_attr.value)]
                    tag.contents = self._translated_refs[tag_original_name]
                    tag_name_attr.value = tag_original_name
        except KeyError as e:
            raise Exception(f'Missing reference {e}')
        
        self.page.text = str(parsed_current_content)
        return self.page
    
    def _apply_translations(self, text: str) -> str:
        for (pattern, replacement) in self._TRANSLATIONS:
            text = re.sub(pattern, replacement, text)
        return text
    
    @run_blocking_io_task
    def save_page(self) -> None:
        if not self._site.logged_in():
            raise Exception("Bot not logged in")
        self.page.save('2.3 Expansão - Atualizando com conteúdo da Wookieepedia', botflag=False)
        
    def get_diff_url(self) -> str:
        return f'{self.page.permalink(self._current_revision, with_protocol=True)}&diff=next'
    
    def _build_reference_dict(self, wikitext: str) -> Dict[str, str]:
        parsed_content: Wikicode = mwparse(wikitext)
        all_refs = self._get_tags_from_wikitext(parsed_content, 'ref')
        return {str(x.get('name').value): str(x.contents) for x in all_refs if x.contents}
        
    def _get_tags_from_wikitext(self, wikitext: Wikicode, tag: str) -> List[Tag]:
        all_tags: List[Tag] = wikitext.filter(forcetype=Tag)
        return [x for x in all_tags if x.tag == tag]
        
    _TRANSLATIONS = [
        # Years-related translations
        ("BBY/Canon", "BBY"),
        ("ABY/Canon", "ABY"),
        (r'\[\[([0-9])([0-9]*) ([BA])BY\|\1\2 \3BY\]\]', r'[[\1\2 \3BY]]'),
        (r'\[\[([0-9])([0-9]*) ABY\]\]', r'[[\1\2 DBY]]'),
        (r'\[\[([0-9])([0-9]*) ABY\|', r'[[\1\2 DBY|'),
        (r'\[\[([0-9])([0-9]*) BBY\]\]', r'[[\1\2 ABY]]'),
        (r'\[\[([0-9])([0-9]*) BBY\|', r'[[\1\2 ABY|'),
        (r'Season ([1-6])', r'Temporada \1'),
        (r'Episode ([0-9])([0-9]|)', r'Episódio \1\2'),
        
        # Labels translations
        ("Unknown placement", "Localização desconhecida"),
        ("\| Year \|", "| Ano |"),
        ("\| Title \|", "| Título |"),
        ("\| Writer\(s\) \|", "| Autor(es) |"),
        ("\| Released\n", "| Lançado em\n"),
        ("\| N \|", "| R |"),
        ("\| C \|", "| Q |"),
        ("\| VG \|", "| J |"),
        ("\| YR \|", "| LI |"),
        ("\| JR \|", "| RIJ |"),
        ("\| Title \|", "| Título |"),
        (r'\|\| ([0-9][0-9][0-9][0-9])-([0-9][0-9])-([0-9][0-9])', r'|| \3/\2/\1'),
        
        # General expressions translations
        ("Young readers adaptation of", "Adaptação infantil de"),
        ("Young-readers adaptation of", "Adaptação infantil de"),
        ("Young adult novelization of", "Romantização de jovens adultos de"),
        ("Game adaptation of", "Game adaptation of"),
        ("Graphic novelization of", "Romantização gráfica de"),
        ("Junior novelization of", "Romantização infanto-juvenil de"),
        ("Game adaptation of", "Adaptação em jogo de"),
        ("Video game adaptation of", "Adaptação em jogo de"),
        ("Comic adaptation of", "Adaptação em quadrinhos de"),
        ("Webcomic adaptation of", "Adaptação em quadrinhos web de"),
        ("Web series adaptation of", "Adaptação de série de web de"),
        ("Chapter book adaptation of", "Adaptação em capítulo de livro de"),
        ("Partial adaptation of", "Adaptação parcial de"),
        ("Young readers partial adaptation of", "Adaptação infantil parcial de"),
        ("Web series partial adaptation of", "Adaptação de série de web parcial de"),
        ("Video game partial adaptation of", "Adaptação em jogo parcial de"),
        ("Novelization of", "Romantização de"),
        ("Adaptation of", "Adaptação de"),
        ("first act of", "primeiro ato de"),
        ("second act of", "segundo ato de"),
        ("third act of", "terceiro ato de"),
        ("Prologue is set immediately before", "Prólogo acontece imediatamente antes de"),
        ("Prologue is set during", "Prólogo acontece durante"),
        ("Prologue is set in", "Prólogo acontece em"),
        ("Prologue occurs in", "Prelúdio ocorre em"),
        ("Prologue is set immediately after", "Prólogo acontece imediatamente depois de"),
        ('Prologue occurs ([1-9])([0-9]|) years prior', r'Prólogo acontece \1\2 anos antes'),
        ("Epilogue is set in", "Epílogo acontece em"),
        ("Epilogue is set immediately before", "Epílogo acontece imediatamente antes de"),
        ("Epilogue is set immediately after", "Epílogo acontece imediatamente depois de"),
        ("Epilogue occurs concurrently with and after", "Epílogo acontece junto com e depois de"),
        ("Epilogue occurs concurrently to", "Epílogo acontece junto com"),
        ("Prologue and epilogue occur briefly before the events of", "Prólogo e epílogo acontecem brevemente antes dos eventos de"),
        ("Prelude occurs concurrently to", "Prelúdio ocorre junto com"),
        ("Prelude occurs at the end of", "Prelúdio ocorre no fim de"),
        ("Prologue and epilogue occur three decades prior", "Prólogo e epílogo acontecem três décadas antes"),
        ("Flashbacks occur in", "Flashbacks ocorrem em"),
        ("Flashbacks take place in", "Flashbacks ocorrem em"),
        ("Flashbacks take place between", "Flashbacks ocorrem entre"),
        ("Occurs before and concurrently with", "Ocorre antes e junto com"),
        ("Occurs prior to and concurrently to", "Ocorre antes e junto com"),
        ("Occurs prior to and concurrently with", "Ocorre antes e junto com"),
        ("Occurs prior to and during", "Ocorre antes e junto com"),
        ("Occurs before, concurrently to, and after", "Ocorre antes, junto com e depois de"),
        ("Occurs before and after", "Ocorre antes e depois de"),
        ("Occurs concurrently to and immediately after", "Ocorre junto com e imediatamente depois de"),
        ("Occurs concurrently to and after", "Ocorre junto com e depois de"),
        ("Occurs concurrently to", "Ocorre junto com"),
        ("Occurs concurrently with", "Ocorre junto com"),
        ("Occurs immediately after", "Ocorre imediatamente depois de"),
        ("and during", "e durante"),
        ("Exact placement currently unknown", "Localização na linha do tempo desconhecida"),
        ("Exact placement of flashback story unknown", "Localização do flashback na linha do tempo desconhecida"),
        ("original trilogy", "trilogia original"),
        ("prequel trilogy", "trilogia prequela"),
        (r'\bde the\b', "de"),
        ("\[\[Forum:SH", "[[:w:c:starwars:Forum:SH"),
        
        (r'cellpadding="4" cellspacing="0" style=".*"', ''),
        
        # Media translations
        (r'\(novel\)', u'(romance)'),
        (r'\(film\)', u'(filme)'),
        (r'\(episode\)', u'(episódio)'),
        (r'\(short story\)', u'(conto)'),
        (r'\bPart\b', u'Parte'),
        (r'\bLost Stars\b', u'Estrelas Perdidas'),
        (r'\bAftermath\b', u'Marcas da Guerra'),
        (r'\bMarcas da Guerra: Life Debt\b', u'Marcas da Guerra: Dívida de Honra'),
        (r'\bMarcas da Guerra: Empire\'s End\b', u'Marcas da Guerra: Fim do Império'),
        (r'\bMarcas da Guerra \(episódio\)', u'Aftermath (episódio)'),
        (r'\bAftermath \(episódio\)\|Marcas da Guerra', u'Aftermath (episódio)|Aftermath'),
        (r'\bSkywalker Strikes\b', u'Skywalker Ataca'),
        (r'\bMoving Target: A Princess Leia Adventure\b', u'Alvo em Movimento: Uma Aventura da Princesa Leia'),
        (r'\bPrincess Leia\b', u'Princesa Leia'),
        (r'\bThe Weapon of a Jedi: A Luke Skywalker Adventure\b', u'A Arma de um Jedi: Uma Aventura de Luke Skywalker'),
        (r'\bSmuggler\'s Run: A Han Solo & Chewbacca Adventure\b', u'A Missão do Contrabandista: Uma Aventura de Han Solo e Chewbacca'),
        (r'\bA New Dawn\b', u'Um Novo Amanhecer'),
        (r'\bLords of the Sith\b', u'Lordes dos Sith'),
        (r'\bTarkin (novel)\b', u'Tarkin (romance)'),
        (r'\bHeir to the Jedi\b', u'Herdeiro do Jedi'),
        (r'\[\[Bloodline \(romance\)\|Bloodline\]\]', u'[[Legado de Sangue]]'),
        (r'Bloodline \(romance\)', u'Legado de Sangue'),
        (r'\bThe Making of Um Novo Amanhecer\b', u'The Making of A New Dawn'),
        (r'\bShattered Empire\b', u'Império Despedaçado'),
        (r'\bThe Inquisitor\'s Trap\b', u'A Armadilha do Inquisidor'),
        (r'\bStar Wars Rebels: Spark of Rebellion\b', u'Star Wars Rebels: A Fagulha de Uma Rebelião'),
        (r'\bDoctor Aphra ([1-9]): Book I\b', r'Doutora Aphra \1: Livro I'),
        (r'\bStar Wars: Uprising\b', u'Star Wars: A Rebelião'),
        (r'\bBattlefront: Twilight Company\b', u'Battlefront: Companhia do Crepúsculo'),
        (r'\bResistance Reborn\b', u'A Resistência Renasce'),
        (r'\bChapter (\d+): ', r'Capítulo \1: '),
        (r'\bStar Wars: Galactic Atlas\b', u'Star Wars: Atlas Galáctico'),
        (r'\bStar Wars: The Rebel Files\b', u'Star Wars: O Arquivo Rebelde'),
        (r'\bThe High Republic: Light of the Jedi', u'The High Republic: Luz dos Jedi'),
        (r'\bStar Wars Biomes\b', u'Star Wars Biomas'),
        (r'\bStar Wars Vehicle Flythroughs\b', u'Por Dentro dos Veículos de Star Wars'),
        (r'\bStar Wars: The Mandalorian Junior Novel\b', u'Star Wars: The Mandalorian (romance juvenil)'),
        (r'\bEmpire of Dreams: The Story of the Star Wars Trilogy\b', u'Império dos Sonhos: A História da Trilogia Star Wars'),
        (r'\[\[Star Wars: Episode I The Phantom Menace\|\'\'Star Wars\'\': Episode I \'\'The Phantom Menace\'\'\]\]', u'{{Filme|I}}'),
        (r'\[\[Star Wars: Episode II Attack of the Clones\|\'\'Star Wars\'\': Episode II \'\'Attack of the Clones\'\'\]\]', u'{{Filme|II}}'),
        (r'\[\[Star Wars: Episode III Revenge of the Sith\|\'\'Star Wars\'\': Episode III \'\'Revenge of the Sith\'\'\]\]', u'{{Filme|III}}'),
        (r'\[\[Star Wars: Episode IV A New Hope\|\'\'Star Wars\'\': Episode IV \'\'A New Hope\'\'\]\]', u'{{Filme|IV}}'),
        (r'\[\[Star Wars: Episode V The Empire Strikes Back\|\'\'Star Wars\'\': Episode V \'\'The Empire Strikes Back\'\'\]\]', u'{{Filme|V}}'),
        (r'\[\[Star Wars: Episode VI Return of the Jedi\|\'\'Star Wars\'\': Episode VI \'\'Return of the Jedi\'\'\]\]', u'{{Filme|VI}}'),
        (r'\[\[Star Wars: Episode VII The Force Awakens\|\'\'Star Wars\'\': Episode VII \'\'The Force Awakens\'\'\]\]', u'{{Filme|VII}}'),
        (r'\[\[Rogue One: A Star Wars Story\]\]', u'[[Rogue One: Uma História Star Wars]]'),
        (r'\[\[Star Wars: Episode VIII The Last Jedi\|\'\'Star Wars\'\': Episode VIII \'\'The Last Jedi\'\'\]\]', u'{{Filme|VIII}}'),
        (r'\[\[Star Wars: Episode IX The Rise of Skywalker\|\'\'Star Wars\'\': Episode IX \'\'The Rise of Skywalker\'\'\]\]', u'{{Filme|IX}}'),
        (r'\[\[Solo: A Star Wars Story\]\]', u'[[Han Solo: Uma História Star Wars]]'),
        (r'Blue Shadow Virus \(episódio\)', u'Blue Shadow Virus'),
        (r'Bounty Hunters \(episódio\)', u'Bounty Hunters'),
        (r'Assassin \(episódio\)', u'Assassin'),
        (r'Altar of Mortis \(episódio\)', u'Altar of Mortis'),
        (r'Bounty \(episódio\)', u'Bounty'),
        (r'Revenge \(episódio\)', u'Revenge'),
        (r'The Gathering \(episódio\)', u'The Gathering'),
        (r'Revival \(episódio\)', u'Revival'),
        (r'Eminence \(episódio\)', u'Eminence'),
        (r'Sabotage \(episódio\)', u'Sabotage'),
        (r'Destiny \(episódio\)', u'Destiny'),
        (r'Empire Day \(episódio\)', u'Empire Day'),
        (r'Idiot\'s Array \(episódio\)', u'Idiot\'s Array'),
        (r'Legacy \(episódio\)', u'Legacy'),
        (r'The General \(episódio\)', u'The General'),
        (r'\bThe Paradise Snare\b', u'A Armadilha do Paraíso'),
        (r'\bDarth Vader and the Cry of Shadows\b', u'Darth Vader: O Clamor das Sombras'),
    ]


if __name__ == "__main__":
    from asyncio import run
    from pywikibot import Page, Site
    
    from dotenv import load_dotenv
    
    async def main():
        logging.basicConfig(level=logging.DEBUG)
        timeline_translator = TimelineTranslator()
        await timeline_translator.get_wookiee_page()
        await timeline_translator.get_timeline_page()
        for ref_name, ref_txt in timeline_translator.build_new_references().items():
            translated_text = input(f'Translate ref {ref_name}: {ref_txt}') or ref_txt
            timeline_translator.add_reference_translation(ref_name, translated_text)
        timeline_translator.translate_page()
        await timeline_translator.login()
        await timeline_translator.save_page()
        print('Page saved. Check the edit diff here: ', timeline_translator.get_diff_url())
    
    load_dotenv()
    
    run(main())
    # python3 -m bot.sww.timeline_translator
