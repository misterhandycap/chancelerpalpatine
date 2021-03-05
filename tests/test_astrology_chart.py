import asyncio
import os
import warnings

from vcr_unittest import VCRTestCase

from bot.astrology.astrology_chart import AstrologyChart
from bot.astrology.exception import AstrologyInvalidInput
from bot.models.astrology_chart import AstrologyChart as AstrologyChartModel
from tests.factories.astrology_chart_factory import AstrologyChartFactory
from tests.support.db_connection import clear_data, Session

class TestAstrologyChart(VCRTestCase):

    @classmethod
    def setUpClass(cls):
        warnings.simplefilter("ignore")
    
    def tearDown(self):
        clear_data(Session())
    
    def test_calc_chart_valid_params(self):
        astrology_chart = AstrologyChart()
        user_id = 14
        date = '1997/08/10'
        time = '07:17'
        city_name = "São Paulo"

        chart = asyncio.run(astrology_chart.calc_chart(user_id, date, time, city_name))
        sun = astrology_chart.get_sun_sign(chart)
        asc = astrology_chart.get_asc_sign(chart)
        moon = astrology_chart.get_moon_sign(chart)

        self.assertEqual(sun, 'Leo')
        self.assertEqual(asc, 'Leo')
        self.assertEqual(moon, 'Scorpio')

    def test_calc_chart_invalid_city(self):
        astrology_chart = AstrologyChart()
        user_id = 14
        date = '1997/08/10'
        time = '07:17'
        city_name = "InvalidCityForSure"

        with self.assertRaises(AstrologyInvalidInput) as e:
            asyncio.run(astrology_chart.calc_chart(user_id, date, time, city_name))
        
        self.assertEqual(e.exception.message, 'City does not exist')

    def test_calc_chart_invalid_date(self):
        astrology_chart = AstrologyChart()
        user_id = 14
        date = 'invalid'
        time = '07:17'
        city_name = "São Paulo"

        with self.assertRaises(AstrologyInvalidInput) as e:
            asyncio.run(astrology_chart.calc_chart(user_id, date, time, city_name))
        
        self.assertIn('Invalid datetime', e.exception.message)

    def test_calc_chart_invalid_time(self):
        astrology_chart = AstrologyChart()
        user_id = 14
        date = '1997/08/10'
        time = 'invalid'
        city_name = "São Paulo"

        with self.assertRaises(AstrologyInvalidInput) as e:
            asyncio.run(astrology_chart.calc_chart(user_id, date, time, city_name))
        
        self.assertIn('Invalid datetime', e.exception.message)

    def test_get_user_chart_user_chart_exists(self):
        astrology_chart = AstrologyChart()
        user_id = 14
        datetime = ('1997/08/10', '07:17', '-03:00')
        geopos = (-23.5506507, -46.6333824)
        chart = astrology_chart.calc_chart_raw(datetime, geopos)
        asyncio.run(astrology_chart.save_chart(user_id, chart))

        result = asyncio.run(astrology_chart.get_user_chart(user_id))

        self.assertEqual(str(chart.date), str(result.date))
        self.assertEqual(str(chart.pos), str(result.pos))

    def test_get_user_chart_user_chart_does_not_exist(self):
        astrology_chart = AstrologyChart()
        AstrologyChartFactory()

        result = asyncio.run(astrology_chart.get_user_chart(98))

        self.assertIsNone(result)

    def test_save_chart(self):
        user_id = 14
        astrology_chart = AstrologyChart()
        datetime = ('1997/08/10', '07:17', '-03:00')
        geopos = (-23.5506507, -46.6333824)
        chart = astrology_chart.calc_chart_raw(datetime, geopos)
        
        result_id = asyncio.run(astrology_chart.save_chart(user_id, chart))

        result = Session().query(AstrologyChartModel).get(result_id)
        self.assertIsNotNone(result)
        self.assertEqual(result.user_id, user_id)
        self.assertEqual(result.datetime.strftime(
            '%Y/%m/%d %H:%M'), f'{datetime[0]} {datetime[1]}') 
        self.assertEqual(result.timezone, '-03:00:00')
        self.assertEqual(result.latitude, geopos[0])
        self.assertEqual(result.longitude, geopos[1])
