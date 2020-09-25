from datetime import datetime

import pytz
from flatlib.chart import Chart
from flatlib.const import HOUSE1, MOON, SUN
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder

def calc_chart(date: str, time: str, city_name: str) -> Chart:
    geopos = get_lat_lng_from_city_name(city_name)
    timezone = get_timezone_from_lat_lng(*geopos, date)
    chart_datetime = Datetime(date, time, timezone)
    chart_geopos = GeoPos(*geopos)
    return Chart(chart_datetime, chart_geopos)

def get_lat_lng_from_city_name(city_name: str):
    geolocator = Nominatim(user_agent='chancelerpalpatine')
    location = geolocator.geocode(city_name)

    return location.latitude, location.longitude

def get_timezone_from_lat_lng(lat: float, lng: float, date: str):
    timezonefinder = TimezoneFinder()
    timezone_name = timezonefinder.timezone_at(lat=lat, lng=lng)
    return pytz.timezone(timezone_name).localize(datetime.strptime(date, '%Y/%m/%d')).strftime('%Z')

def get_sun_sign(chart: Chart) -> str:
    return chart.getObject(SUN).sign

def get_asc_sign(chart: Chart) -> str:
    return chart.get(HOUSE1).sign

def get_moon_sign(chart: Chart) -> str:
    return chart.getObject(MOON).sign

