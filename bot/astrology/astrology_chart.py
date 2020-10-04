import pickle
from datetime import datetime

import pytz
from flatlib.chart import Chart
from flatlib.const import HOUSE1, MOON, SUN
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from geopy.adapters import AioHTTPAdapter
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder

from bot.astrology.exception import AstrologyInvalidInput
from bot.astrology.user_chart import UserChart


class AstrologyChart():

    def __init__(self, pickle_filename='astrology_charts.pickle'):
        self.pickle_filename = pickle_filename
        self.charts = []

    def load_charts(self):
        try:
            with open(self.pickle_filename, 'rb') as f:
                self.charts = pickle.load(f)
        except FileNotFoundError:
            self.charts = []
        finally:
            return self.charts
    
    def get_user_chart(self, user_id: str):
        return next((uc for uc in self.charts if uc.user_id == str(user_id)), None)
    
    async def calc_chart(self, user_id: str, date: str, time: str, city_name: str) -> Chart:
        geopos = await self._get_lat_lng_from_city_name(city_name)
        timezone = self._get_timezone_from_lat_lng(*geopos, f'{date} {time}')
        
        chart = self.calc_chart_raw((date, time, timezone), geopos)
        
        self._remove_user_s_charts(user_id)
        user_chart = UserChart(user_id, chart)
        self.charts.append(user_chart)
        self.save_charts()
        return chart

    def calc_chart_raw(self, datetime: tuple, geopos: tuple):
        chart_datetime = Datetime(*datetime)
        chart_geopos = GeoPos(*geopos)
        return Chart(chart_datetime, chart_geopos)

    def get_sun_sign(self, chart: Chart) -> str:
        return chart.getObject(SUN).sign

    def get_asc_sign(self, chart: Chart) -> str:
        return chart.get(HOUSE1).sign

    def get_moon_sign(self, chart: Chart) -> str:
        return chart.getObject(MOON).sign

    def save_charts(self):
        with open(self.pickle_filename, 'wb') as f:
            pickle.dump(self.charts, f)

    async def _get_lat_lng_from_city_name(self, city_name: str):
        async with Nominatim(
                user_agent='chancelerpalpatine', adapter_factory=AioHTTPAdapter) as geolocator:
            location = await geolocator.geocode(city_name)
            if not location:
                raise AstrologyInvalidInput('Cidade não existe')

            return location.latitude, location.longitude

    def _get_timezone_from_lat_lng(self, lat: float, lng: float, dt: str):
        timezonefinder = TimezoneFinder()
        timezone_name = timezonefinder.timezone_at(lat=lat, lng=lng)
        try:
            return pytz.timezone(timezone_name).localize(
                datetime.strptime(dt, '%Y/%m/%d %H:%M')).strftime('%Z')
        except ValueError:
            raise AstrologyInvalidInput('Data e/ou hora inválida(s). Formato esperado: `%Y/%m/%d %H:%M`')

    def _remove_user_s_charts(self, user_id):
        self.charts = [uc for uc in self.charts if uc.user_id != str(user_id)]

