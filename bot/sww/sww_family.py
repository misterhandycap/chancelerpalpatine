from pywikibot import family


class StarWarsWikiFamily(family.Family):
    name = 'starwarsfandom'
    langs = {
        'pt': 'starwars.fandom.com',
    }

    def protocol(self, code):
        return 'https'

    def scriptpath(self, code):
        return {
            'pt': '/pt',
        }[code]

    def version(self, code):
        return {
            'pt': u'1.39.3',
        }[code]
