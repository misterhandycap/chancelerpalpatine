import pickle
import os
from unittest import TestCase

from bot.astrology.astrology_chart import AstrologyChart
from bot.astrology.user_chart import UserChart

PICKLE_FILENAME = 'astrology_charts_test.pickle'


class TestAstrologyChart(TestCase):

    def tearDown(self):
        try:
            os.remove(PICKLE_FILENAME)
        except FileNotFoundError:
            pass
    
    def test_calc_chart(self):
        astrology_chart = AstrologyChart()
        user_id = 14
        date = '1997/08/10'
        time = '07:17'
        city_name = "São Paulo"

        chart = astrology_chart.calc_chart(user_id, date, time, city_name)
        sun = astrology_chart.get_sun_sign(chart)
        asc = astrology_chart.get_asc_sign(chart)
        moon = astrology_chart.get_moon_sign(chart)

        self.assertEqual(sun, 'Leo')
        self.assertEqual(asc, 'Leo')
        self.assertEqual(moon, 'Scorpio')

    def test_get_user_chart_user_chart_exists(self):
        user_id = 14
        astrology_chart = AstrologyChart(pickle_filename=PICKLE_FILENAME)
        datetime = ('1997/08/10', '07:17', '-03:00')
        geopos = (-23.5506507, -46.6333824)
        chart = astrology_chart.calc_chart_raw(datetime, geopos)
        user_chart = UserChart(user_id, chart)
        astrology_chart.charts.append(user_chart)

        result = astrology_chart.get_user_chart(user_id)

        self.assertEqual(result, user_chart)

    def test_get_user_chart_user_chart_does_not_exist(self):
        user_id = 14
        astrology_chart = AstrologyChart(pickle_filename=PICKLE_FILENAME)
        datetime = ('1997/08/10', '07:17', '-03:00')
        geopos = (-23.5506507, -46.6333824)
        chart = astrology_chart.calc_chart_raw(datetime, geopos)
        user_chart = UserChart(user_id, chart)
        astrology_chart.charts.append(user_chart)

        result = astrology_chart.get_user_chart(98)

        self.assertIsNone(result)

    def test_load_charts_file_exists(self):
        astrology_chart = AstrologyChart(pickle_filename=PICKLE_FILENAME)
        datetime = ('1997/08/10', '07:17', '-03:00')
        geopos = (-23.5506507, -46.6333824)
        chart = astrology_chart.calc_chart_raw(datetime, geopos)
        user_chart = UserChart(user_id='14', chart=chart)

        with open(PICKLE_FILENAME, 'wb') as f:
            pickle.dump([user_chart], f)

        self.assertEqual(astrology_chart.charts, [])

        astrology_chart.load_charts()

        self.assertListEqual(astrology_chart.charts, [user_chart])
    
    def test_load_charts_file_does_not_exist(self):
        astrology_chart = AstrologyChart(pickle_filename=PICKLE_FILENAME)
        self.assertEqual(astrology_chart.charts, [])

    def test_save_charts(self):
        astrology_chart = AstrologyChart(pickle_filename=PICKLE_FILENAME)
        datetime = ('1997/08/10', '07:17', '-03:00')
        geopos = (-23.5506507, -46.6333824)
        chart = astrology_chart.calc_chart_raw(datetime, geopos)
        user_chart = UserChart(user_id=14, chart=chart)
        astrology_chart.charts.append(user_chart)

        astrology_chart.save_charts()

        with open(PICKLE_FILENAME, 'rb') as f:
            self.assertListEqual(astrology_chart.charts, pickle.load(f))
