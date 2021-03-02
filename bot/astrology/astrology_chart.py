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
from bot.models.astrology_chart import AstrologyChart as AstrologyChartModel
from bot.models.user import User


class AstrologyChart():

    async def get_user_chart(self, user_id: str):
        astrology_chart = await AstrologyChartModel.get_by_user_id(user_id)
        if not astrology_chart:
            return None

        chart_datetime = (
            [
                astrology_chart.datetime.year,
                astrology_chart.datetime.month,
                astrology_chart.datetime.day
            ],
            [
                '+',
                astrology_chart.datetime.hour,
                astrology_chart.datetime.minute,
                astrology_chart.datetime.second
            ],
            astrology_chart.timezone
        )
        chart_geopos = (astrology_chart.latitude, astrology_chart.longitude)
        return self.calc_chart_raw(chart_datetime, chart_geopos)
    
    async def calc_chart(self, user_id: str, date: str, time: str, city_name: str) -> Chart:
        geopos = await self._get_lat_lng_from_city_name(city_name)
        timezone = self._get_timezone_from_lat_lng(*geopos, f'{date} {time}')
        
        return self.calc_chart_raw((date, time, timezone), geopos)

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

    async def save_chart(self, user_id: str, chart: Chart) -> str:
        astrology_chart = await AstrologyChartModel.get_by_user_id(user_id) or AstrologyChartModel()
        astrology_chart.user = await User.get(user_id) or User(id=user_id)
        astrology_chart.datetime = datetime(
            chart.date.date.toList()[1],
            chart.date.date.toList()[2],
            chart.date.date.toList()[3],
            chart.date.time.toList()[1],
            chart.date.time.toList()[2],
        )
        astrology_chart.timezone = chart.date.utcoffset.toString()
        astrology_chart.latitude = chart.pos.lat
        astrology_chart.longitude = chart.pos.lon
        
        return await AstrologyChartModel.save(astrology_chart)

    async def _get_lat_lng_from_city_name(self, city_name: str):
        async with Nominatim(
                user_agent='chancelerpalpatine', adapter_factory=AioHTTPAdapter) as geolocator:
            location = await geolocator.geocode(city_name)
            if not location:
                raise AstrologyInvalidInput('City does not exist')

            return location.latitude, location.longitude

    def _get_timezone_from_lat_lng(self, lat: float, lng: float, dt: str):
        timezonefinder = TimezoneFinder()
        timezone_name = timezonefinder.timezone_at(lat=lat, lng=lng)
        try:
            return pytz.timezone(timezone_name).localize(
                datetime.strptime(dt, '%Y/%m/%d %H:%M')).strftime('%Z')
        except ValueError:
            raise AstrologyInvalidInput('Invalid datetime. Expected format: `%Y/%m/%d %H:%M`')

    def _remove_user_s_charts(self, user_id):
        self.charts = [uc for uc in self.charts if uc.user_id != str(user_id)]

