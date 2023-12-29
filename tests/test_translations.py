from bot.sww.translations import JSONTranslationsUpdater
from tests.support.pywikibot_test_case import PywikibotTestCase


class TestJSONTranslationsUpdater(PywikibotTestCase):
    def test_get_translations_json_dump(self):
        translations_updater = JSONTranslationsUpdater()
        
        result = translations_updater.get_translations_json_dump()
        
        self.assertEqual(result, """<pre>{
    "regex": true,
    "msg": {
        "_default": "([[User:Thales César|Thales]]) Varredura padrão: obras"
    },
    "replacements": [
        [
            "\\\\(novel\\\\)",
            "(romance)"
        ],
        [
            "\\\\(film\\\\)",
            "(filme)"
        ],
        [
            "\\\\(episode\\\\)",
            "(episódio)"
        ],
        [
            "\\\\(short story\\\\)",
            "(conto)"
        ],
        [
            "\\\\bPart\\\\b",
            "Parte"
        ],
        [
            "\\\\bLost Stars\\\\b",
            "Estrelas Perdidas"
        ],
        [
            "\\\\bAftermath\\\\b",
            "Marcas da Guerra"
        ],
        [
            "\\\\bMarcas da Guerra: Life Debt\\\\b",
            "Marcas da Guerra: Dívida de Honra"
        ],
        [
            "\\\\bMarcas da Guerra: Empire\\\\'s End\\\\b",
            "Marcas da Guerra: Fim do Império"
        ],
        [
            "\\\\bMarcas da Guerra \\\\(episódio\\\\)",
            "Aftermath (episódio)"
        ],
        [
            "\\\\bAftermath \\\\(episódio\\\\)\\\\|Marcas da Guerra",
            "Aftermath (episódio)|Aftermath"
        ],
        [
            "\\\\bSkywalker Strikes\\\\b",
            "Skywalker Ataca"
        ],
        [
            "\\\\bMoving Target: A Princess Leia Adventure\\\\b",
            "Alvo em Movimento: Uma Aventura da Princesa Leia"
        ],
        [
            "\\\\bPrincess Leia\\\\b",
            "Princesa Leia"
        ],
        [
            "\\\\bThe Weapon of a Jedi: A Luke Skywalker Adventure\\\\b",
            "A Arma de um Jedi: Uma Aventura de Luke Skywalker"
        ],
        [
            "\\\\bSmuggler\\\\'s Run: A Han Solo & Chewbacca Adventure\\\\b",
            "A Missão do Contrabandista: Uma Aventura de Han Solo e Chewbacca"
        ],
        [
            "\\\\bA New Dawn\\\\b",
            "Um Novo Amanhecer"
        ],
        [
            "\\\\bLords of the Sith\\\\b",
            "Lordes dos Sith"
        ],
        [
            "\\\\bTarkin (novel)\\\\b",
            "Tarkin (romance)"
        ],
        [
            "\\\\bHeir to the Jedi\\\\b",
            "Herdeiro do Jedi"
        ],
        [
            "\\\\[\\\\[Bloodline \\\\(romance\\\\)\\\\|Bloodline\\\\]\\\\]",
            "[[Legado de Sangue]]"
        ],
        [
            "Bloodline \\\\(romance\\\\)",
            "Legado de Sangue"
        ],
        [
            "\\\\bThe Making of Um Novo Amanhecer\\\\b",
            "The Making of A New Dawn"
        ],
        [
            "\\\\bShattered Empire\\\\b",
            "Império Despedaçado"
        ],
        [
            "\\\\bThe Inquisitor\\\\'s Trap\\\\b",
            "A Armadilha do Inquisidor"
        ],
        [
            "\\\\bStar Wars Rebels: Spark of Rebellion\\\\b",
            "Star Wars Rebels: A Fagulha de Uma Rebelião"
        ],
        [
            "\\\\bDoctor Aphra ([1-9]): Book I\\\\b",
            "Doutora Aphra $1: Livro I"
        ],
        [
            "\\\\bStar Wars: Uprising\\\\b",
            "Star Wars: A Rebelião"
        ],
        [
            "\\\\bBattlefront: Twilight Company\\\\b",
            "Battlefront: Companhia do Crepúsculo"
        ],
        [
            "\\\\bResistance Reborn\\\\b",
            "A Resistência Renasce"
        ],
        [
            "\\\\bChapter (\\\\d+): ",
            "Capítulo $1: "
        ],
        [
            "\\\\bStar Wars: Galactic Atlas\\\\b",
            "Star Wars: Atlas Galáctico"
        ],
        [
            "\\\\bStar Wars: The Rebel Files\\\\b",
            "Star Wars: O Arquivo Rebelde"
        ],
        [
            "\\\\bThe High Republic: Light of the Jedi",
            "The High Republic: Luz dos Jedi"
        ],
        [
            "\\\\bStar Wars Biomes\\\\b",
            "Star Wars Biomas"
        ],
        [
            "\\\\bStar Wars Vehicle Flythroughs\\\\b",
            "Por Dentro dos Veículos de Star Wars"
        ],
        [
            "\\\\bStar Wars: The Mandalorian Junior Novel\\\\b",
            "Star Wars: The Mandalorian (romance juvenil)"
        ],
        [
            "\\\\bEmpire of Dreams: The Story of the Star Wars Trilogy\\\\b",
            "Império dos Sonhos: A História da Trilogia Star Wars"
        ],
        [
            "\\\\[\\\\[Star Wars: Episode I The Phantom Menace\\\\|\\\\'\\\\'Star Wars\\\\'\\\\': Episode I \\\\'\\\\'The Phantom Menace\\\\'\\\\'\\\\]\\\\]",
            "{{Filme|I}}"
        ],
        [
            "\\\\[\\\\[Star Wars: Episode II Attack of the Clones\\\\|\\\\'\\\\'Star Wars\\\\'\\\\': Episode II \\\\'\\\\'Attack of the Clones\\\\'\\\\'\\\\]\\\\]",
            "{{Filme|II}}"
        ],
        [
            "\\\\[\\\\[Star Wars: Episode III Revenge of the Sith\\\\|\\\\'\\\\'Star Wars\\\\'\\\\': Episode III \\\\'\\\\'Revenge of the Sith\\\\'\\\\'\\\\]\\\\]",
            "{{Filme|III}}"
        ],
        [
            "\\\\[\\\\[Star Wars: Episode IV A New Hope\\\\|\\\\'\\\\'Star Wars\\\\'\\\\': Episode IV \\\\'\\\\'A New Hope\\\\'\\\\'\\\\]\\\\]",
            "{{Filme|IV}}"
        ],
        [
            "\\\\[\\\\[Star Wars: Episode V The Empire Strikes Back\\\\|\\\\'\\\\'Star Wars\\\\'\\\\': Episode V \\\\'\\\\'The Empire Strikes Back\\\\'\\\\'\\\\]\\\\]",
            "{{Filme|V}}"
        ],
        [
            "\\\\[\\\\[Star Wars: Episode VI Return of the Jedi\\\\|\\\\'\\\\'Star Wars\\\\'\\\\': Episode VI \\\\'\\\\'Return of the Jedi\\\\'\\\\'\\\\]\\\\]",
            "{{Filme|VI}}"
        ],
        [
            "\\\\[\\\\[Star Wars: Episode VII The Force Awakens\\\\|\\\\'\\\\'Star Wars\\\\'\\\\': Episode VII \\\\'\\\\'The Force Awakens\\\\'\\\\'\\\\]\\\\]",
            "{{Filme|VII}}"
        ],
        [
            "\\\\[\\\\[Rogue One: A Star Wars Story\\\\]\\\\]",
            "[[Rogue One: Uma História Star Wars]]"
        ],
        [
            "\\\\[\\\\[Star Wars: Episode VIII The Last Jedi\\\\|\\\\'\\\\'Star Wars\\\\'\\\\': Episode VIII \\\\'\\\\'The Last Jedi\\\\'\\\\'\\\\]\\\\]",
            "{{Filme|VIII}}"
        ],
        [
            "\\\\[\\\\[Star Wars: Episode IX The Rise of Skywalker\\\\|\\\\'\\\\'Star Wars\\\\'\\\\': Episode IX \\\\'\\\\'The Rise of Skywalker\\\\'\\\\'\\\\]\\\\]",
            "{{Filme|IX}}"
        ],
        [
            "\\\\[\\\\[Solo: A Star Wars Story\\\\]\\\\]",
            "[[Han Solo: Uma História Star Wars]]"
        ],
        [
            "Blue Shadow Virus \\\\(episódio\\\\)",
            "Blue Shadow Virus"
        ],
        [
            "Bounty Hunters \\\\(episódio\\\\)",
            "Bounty Hunters"
        ],
        [
            "Assassin \\\\(episódio\\\\)",
            "Assassin"
        ],
        [
            "Altar of Mortis \\\\(episódio\\\\)",
            "Altar of Mortis"
        ],
        [
            "Bounty \\\\(episódio\\\\)",
            "Bounty"
        ],
        [
            "Revenge \\\\(episódio\\\\)",
            "Revenge"
        ],
        [
            "The Gathering \\\\(episódio\\\\)",
            "The Gathering"
        ],
        [
            "Revival \\\\(episódio\\\\)",
            "Revival"
        ],
        [
            "Eminence \\\\(episódio\\\\)",
            "Eminence"
        ],
        [
            "Sabotage \\\\(episódio\\\\)",
            "Sabotage"
        ],
        [
            "Destiny \\\\(episódio\\\\)",
            "Destiny"
        ],
        [
            "Empire Day \\\\(episódio\\\\)",
            "Empire Day"
        ],
        [
            "Idiot\\\\'s Array \\\\(episódio\\\\)",
            "Idiot's Array"
        ],
        [
            "Legacy \\\\(episódio\\\\)",
            "Legacy"
        ],
        [
            "The General \\\\(episódio\\\\)",
            "The General"
        ],
        [
            "\\\\bThe Paradise Snare\\\\b",
            "A Armadilha do Paraíso"
        ],
        [
            "\\\\bDarth Vader and the Cry of Shadows\\\\b",
            "Darth Vader: O Clamor das Sombras"
        ],
        [
            "{{[Ii]ncomplete list}}",
            "{{Lista-completa}}"
        ],
        [
            "{{[Mm]ore sources}}",
            "{{Fontes}}"
        ],
        [
            "{{Film\\\\|",
            "{{Filme|"
        ]
    ]
}</pre>""")
