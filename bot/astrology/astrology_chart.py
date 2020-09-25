from flatlib.chart import Chart
from flatlib.const import HOUSE1, MOON, SUN
from flatlib.datetime import Datetime
from flatlib.geopos import GeoPos

def calc_chart(datetime: tuple, geopos: tuple):
    chart_datetime = Datetime(*datetime)
    chart_geopos = GeoPos(*geopos)
    return Chart(chart_datetime, chart_geopos)

def get_sun_sign(chart: Chart):
    return chart.getObject(SUN).sign

def get_asc_sign(chart: Chart):
    return chart.get(HOUSE1).sign

def get_moon_sign(chart: Chart):
    return chart.getObject(MOON).sign

