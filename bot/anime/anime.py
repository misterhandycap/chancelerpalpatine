from mal import Anime as MalAnime
from mal import AnimeSearch


class Anime():

    def __init__(self):
        self.timeout = 10

    def get_anime(self, mal_id):
        try:
            return MalAnime(mal_id, timeout=self.timeout)
        except Exception as e:
            print(e)
            return None
    
    def search_anime(self, query):
        try:
            search = AnimeSearch(query, timeout=self.timeout)

            return [x.__dict__ for x in search.results]
        except Exception as e:
            print(e)
            return None
