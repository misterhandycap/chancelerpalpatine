from unittest import TestCase

from bot.astrology.astrology_chart import calc_chart, get_asc_sign, get_moon_sign, get_sun_sign


class TestAstrologyChart(TestCase):

    def test_calc_chart(self):
        date = '1997/08/10'
        time = '07:17'
        city_name = "São Paulo"

        chart = calc_chart(date, time, city_name)
        sun = get_sun_sign(chart)
        asc = get_asc_sign(chart)
        moon = get_moon_sign(chart)

        self.assertEqual(sun, 'Leo')
        self.assertEqual(asc, 'Leo')
        self.assertEqual(moon, 'Scorpio')
