import os
from unittest import TestCase

from bot.across_the_stars.planets import Planets
from bot.models.planets import Planet
from tests.support.db_connection import clear_data, Session

class TestPlanets(TestCase):

    def test_list_of_planets(self):
        session = Session()
        planet = Planet()
        planet.name = 'Tatooine'
        planet.happines_base = 50
        planet.importance_base = 30
        planet.price = 75000
        planet.region = 'Orla Exterior'
        planet.climate = 'Desértico'
        planet.circuference = 100000
        planet.mass = 100000
        session.add(planet)
        session.commit()
