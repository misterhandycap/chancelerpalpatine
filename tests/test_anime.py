from unittest import TestCase

from bot.anime.anime import Anime


class TestAnime(TestCase):
    
    def test_get_anime(self):
        anime_bot = Anime()

        actual = anime_bot.get_anime(4181)

        self.assertEqual(actual.title, "Clannad: After Story")
        self.assertEqual(actual.title_english, "Clannad ~After Story~")
        self.assertEqual(actual.title_japanese, "CLANNAD〜AFTER STORY〜 クラナド アフターストーリー")
        self.assertEqual(actual.image_url, "https://cdn.myanimelist.net/images/anime/13/24647.jpg")
        self.assertEqual(actual.rating, "PG-13 - Teens 13 or older")
        self.assertEqual(actual.genres, ["Slice of Life", "Comedy", "Supernatural", "Drama", "Romance"])
        self.assertIn(int(actual.score), range(0, 10))
        self.assertIn("Clannad: After Story, the sequel to the critically acclaimed", actual.synopsis)
        self.assertEqual(actual.url, "https://myanimelist.net/anime/4181/Clannad__After_Story")
    
    def test_search_anime(self):
        anime_bot = Anime()

        actual = anime_bot.search_anime("clannad")

        for result in actual:
            self.assertIn("mal_id", result)
            self.assertIn("url", result)
            self.assertIn("image_url", result)
            self.assertIn("title", result)
            self.assertIn("synopsis", result)
            self.assertIn("type", result)
            self.assertIn("episodes", result)
            self.assertIn("score", result)
