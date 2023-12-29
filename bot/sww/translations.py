import json

from pywikibot import Page

from bot.sww.wiki_bot import WikiBot
from bot.utils import run_blocking_io_task


MEDIA_TRANSLATIONS = [
    # Helpers
    (r'\(novel\)', u'(romance)'),
    (r'\(film\)', u'(filme)'),
    (r'\(episode\)', u'(episódio)'),
    (r'\(short story\)', u'(conto)'),
    (r'\bPart\b', u'Parte'),
    
    # Cânon
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
    
    # Films
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
    
    # TV episodes
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
    
    # Legends
    (r'\bThe Paradise Snare\b', u'A Armadilha do Paraíso'),
    (r'\bDarth Vader and the Cry of Shadows\b', u'Darth Vader: O Clamor das Sombras'),
]
WOOKIEE_TRANSLATIONS = [
    (r'{{[Ii]ncomplete list}}', '{{Lista-completa}}'),
    (r'{{[Mm]ore sources}}', '{{Fontes}}'),
    (r'{{Film\|', u'{{Filme|'),
]


class JSONTranslationsUpdater(WikiBot):
    def get_translations_json_dump(self) -> str:
        legacy_fixes = {'regex': True, 'msg': {'_default': '([[User:Thales César|Thales]]) Varredura padrão: obras'}}
        fixes = {**legacy_fixes, 'replacements': MEDIA_TRANSLATIONS + WOOKIEE_TRANSLATIONS}
        fixes_json = json.dumps(fixes, ensure_ascii=False, indent=4)
        return "<pre>{}</pre>".format(fixes_json.replace('\\\\1', '$1'))
    
    @run_blocking_io_task
    def get_page(self) -> Page:
        self.page = Page(self.site, "Star Wars Wiki:Apêndice de Tradução de obras/JSON")
        return self.page
    
    @run_blocking_io_task
    def update_json_page(self, content: str):
        self.page.text = content
        self.page.save("Atualizando com novo conteúdo")
        

if __name__ == "__main__":
    from asyncio import run
    
    from dotenv import load_dotenv
    from pywikibot import showDiff
    
    async def main():
        translations_updater = JSONTranslationsUpdater()
        await translations_updater.get_site()
        await translations_updater.get_page()
        await translations_updater.login()
        content = translations_updater.get_translations_json_dump()
        showDiff(translations_updater.page.text, content)
        input('Press enter to save. Interrupt to abort.')
        await translations_updater.update_json_page(content)
    
    load_dotenv()
    
    run(main())
