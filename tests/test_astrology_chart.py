from unittest import TestCase

from bot.astrology.astrology_chart import calc_chart, get_asc_sign, get_moon_sign, get_sun_sign


class TestAstrologyChart(TestCase):

    def test_calc_chart(self):
        datetime = ('1997/08/10', '07:17', '-03:00')
        geopos = (-23.5489, -46.6388)

        chart = calc_chart(datetime, geopos)
        sun = get_sun_sign(chart)
        asc = get_asc_sign(chart)
        moon = get_moon_sign(chart)

        self.assertEqual(sun, 'Leo')
        self.assertEqual(asc, 'Leo')
        self.assertEqual(moon, 'Scorpio')
