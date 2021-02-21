import asyncio
import os
from unittest import TestCase

from bot.across_the_stars.planets import Planets
from bot.models.planets import Planet
from tests.support.db_connection import clear_data, Session

class TestPlanets(TestCase):

    def setUp(self):
        self.db_session = Session()
    
    def tearDown(self):
        clear_data(self.db_session)
        self.db_session.close()
    
    def test_list_of_planets_region_exists(self):
        for i in range(6):
            planet = Planet()
            planet.name = 'Planeta esperado' if i%2 else 'Planeta não esperado'
            planet.happines_base = 50
            planet.importance_base = 30
            planet.price = 75000
            planet.region = 'Orla Exterior' if i%2 else 'Núcleo'
            planet.climate = 'Desértico'
            planet.circuference = 100000
            self.db_session.add(planet)
        self.db_session.commit()

        result = asyncio.run(Planets().list_of_planets(region='Orla Exterior'))

        self.assertEqual(len(result), 3)
        self.assertEqual(result[0].name, 'Planeta esperado')
        self.assertEqual(result[1].name, 'Planeta esperado')
        self.assertEqual(result[2].name, 'Planeta esperado')

    def test_list_of_planets_region_does_not_exist(self):
        for i in range(6):
            planet = Planet()
            planet.name = 'Planeta esperado' if i%2 else 'Planeta não esperado'
            planet.happines_base = 50
            planet.importance_base = 30
            planet.price = 75000
            planet.region = 'Orla Exterior' if i%2 else 'Núcleo'
            planet.climate = 'Desértico'
            planet.circuference = 100000
            self.db_session.add(planet)
        self.db_session.commit()

        result = asyncio.run(Planets().list_of_planets(region='Orla Média'))

        self.assertEqual(result, [])

    def test_list_of_planets_no_filters(self):
        for i in range(6):
            planet = Planet()
            planet.name = 'Planeta esperado' if i%2 else 'Planeta não esperado'
            planet.happines_base = 50
            planet.importance_base = 30
            planet.price = 75000
            planet.region = 'Orla Exterior' if i%2 else 'Núcleo'
            planet.climate = 'Desértico'
            planet.circuference = 100000
            self.db_session.add(planet)
        self.db_session.commit()

        result = asyncio.run(Planets().list_of_planets())

        self.assertEqual(len(result), 6)
