import logging
import re
from hashlib import md5
from typing import Dict, List

from aiohttp import ClientSession, ClientResponseError
from pywikibot import config, Page
from mwparserfromhell import parse as mwparse
from mwparserfromhell.wikicode import Wikicode
from mwparserfromhell.nodes.tag import Tag

from bot.sww.translations import MEDIA_TRANSLATIONS
from bot.sww.wiki_bot import WikiBot
from bot.utils import run_blocking_io_task


class TimelineTranslator(WikiBot):
    WOOKIEE_TIMELINE_URL = "http://starwars.wikia.com/wiki/Timeline_of_canon_media?action=raw"
    
    def __init__(self, auto_close_session: bool=False) -> None:
        self.auto_close_session = auto_close_session
        self.client_session: ClientSession = None
        self.page: Page = None
        self._original_content: str = None
        self._current_content: str = None
        self._translated_refs: Dict[str, str] = {}
        self._current_revision: int = None
        config.put_throttle = 1
        super().__init__()
        
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
        self.page = Page(self.site, u"Linha do tempo de mídia canônica")
        self._current_content = self.page.text
        self._current_revision = self.page.latest_revision_id
        return self.page
                
    def build_new_references(self) -> Dict[str, str]:
        if not self._original_content or not self._current_content:
            raise Exception("Load both Wookieepedia and SWW content first")
        
        original_refs = self._build_reference_dict(self._original_content)
        current_refs = self._build_reference_dict(self._current_content)
        self._translated_refs = current_refs
        
        all_original_refs = self._get_tags_from_wikitext(mwparse(self._original_content), 'ref')
        for tag in all_original_refs:
            if not tag.has("name") and tag.contents:
                translated_contents = self._apply_translations(str(tag.contents))
                original_refs[self._md5(translated_contents)] = str(tag.contents)
        
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
                if not tag.contents:
                    continue
                tag_name_attr = tag.get("name") if tag.has("name") else tag.add("name", self._md5(str(tag.contents)))
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
        if not self.site.logged_in():
            raise Exception("Bot not logged in")
        self.page.save('2.3 Expansão - Atualizando com conteúdo da Wookieepedia', botflag=False)
        
    def get_diff_url(self) -> str:
        return f'{self.page.permalink(self._current_revision, with_protocol=True)}&diff=next'
    
    def _build_reference_dict(self, wikitext: str) -> Dict[str, str]:
        parsed_content: Wikicode = mwparse(wikitext)
        all_refs = self._get_tags_from_wikitext(parsed_content, 'ref')
        return {str(x.get("name").value): str(x.contents) for x in all_refs if x.contents and x.has("name")}
        
    def _get_tags_from_wikitext(self, wikitext: Wikicode, tag: str) -> List[Tag]:
        all_tags: List[Tag] = wikitext.filter(forcetype=Tag)
        return [x for x in all_tags if x.tag == tag]
    
    def _md5(self, text: str) -> str:
        return md5(text.encode()).hexdigest()
        
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
    ] + MEDIA_TRANSLATIONS


if __name__ == "__main__":
    from asyncio import run
    from pywikibot import Page
    
    from dotenv import load_dotenv
    
    async def main():
        logging.basicConfig(level=logging.DEBUG)
        timeline_translator = TimelineTranslator()
        await timeline_translator.get_site()
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
