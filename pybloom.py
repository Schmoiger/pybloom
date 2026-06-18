"""
Weather station - Technical stories:
1) Check current weather
2) Assign colour depending on temperature
3) Change colour of Philips Hue Bloom to display temperature
4) Log the weather reading
5) Make Hue colours available from external SQL database
6) Calculate data points from observation
7) Run every hour
8) Visualisation
9) Serve page in local network

Technologies used:
- Python: main scripting language
- OpenWeatherMap API: gather weather information
- Philips Hue API: set lights colours
- SQLite3: database
- pyGal: lightweight graphing library
- Flask: framework for website
- Jinja2: scripting language for Flask
- HTML5: basic structure of website
- Bootstrap CSS: framework for CSS
- JavaScript: interactive features of website
- Advanced Python Scheduler: periodic running of script

Notes:
- Program is intended to be called periodically
- Logged data is persistent
- Using free versions of all API, so there is limit to number of calls
"""
from datetime import datetime, timedelta
import logging
from statistics import mean
from typing import TypedDict, cast

import qhue
from rgbxy import Converter
from rgbxy import GamutA
from dateutil.relativedelta import relativedelta
import pyowm
import pygal
from pygal.style import Style
from db_utils import db_connect, get_rows
import credentials

logger = logging.getLogger(__name__)


class HueLampState(TypedDict):
    on: bool
    xy: tuple[float, float]


class HueLampData(TypedDict):
    state: HueLampState
    name: str

DATETIME_STRING = '%Y-%m-%d %H:%M:%S'
FILEPATH = './app/static/'
OWM_KEY = credentials.credentials['owm_key']
HUE_USERNAME = credentials.credentials['hue_username']
HUE_IP = credentials.credentials['hue_ip']
HOME_LOCATION = credentials.credentials['home_location']


class WeatherObservation:
    """Current weather observation fetched from OpenWeatherMap."""

    def __init__(
        self,
        timestamp: str | None = None,
        temperature: float | None = None,
        detailed_status: str | None = None,
    ) -> None:
        self.timestamp = timestamp
        self.temperature = temperature
        self.detailed_status = detailed_status

    def __str__(self) -> str:
        return f'Current weather: {self.detailed_status}, {self.temperature} celsius (made at {self.timestamp})'

    def fetch(self, location: str) -> str:  # expect e.g. 'London, GB'
        try:
            owm = pyowm.OWM(OWM_KEY)
            mgr = owm.weather_manager()
            observation = mgr.weather_at_place(location)
            if observation is None:
                raise RuntimeError(f'No observation returned for {location}')
            weather_reading = observation.weather
            if weather_reading is None:
                raise RuntimeError(f'No weather reading returned for {location}')
            self.timestamp = datetime.now().strftime(DATETIME_STRING)
            self.temperature = weather_reading.temperature('celsius')['temp']
            self.detailed_status = weather_reading.detailed_status
            return 'Fetched new observation'
        except Exception:
            logger.exception('Failed to fetch weather for %s', location)
            raise

    def log(self) -> str:
        con = db_connect()
        cur = con.cursor()

        try:
            sql = '''INSERT INTO observations (timestamp,
                                               temperature,
                                               detailed_status)
                     VALUES (?, ?, ?)'''
            cur.execute(sql, (self.timestamp,
                              self.temperature,
                              self.detailed_status))
            con.commit()
            return 'Observation logged'
        finally:
            con.close()

    def set(self, timestamp: str, temperature: float, detailed_status: str) -> str:  # for debug
        self.timestamp = timestamp
        self.temperature = temperature
        self.detailed_status = detailed_status
        return 'Observation set'


class HueLamp:
    """Thin wrapper around a single Hue light."""

    def __init__(self, lamp_id: int) -> None:
        try:
            ip = HUE_IP
            username = HUE_USERNAME
            self.bridge = qhue.Bridge(ip, username)
            self.getter = cast(HueLampData, self.bridge.lights[lamp_id]())
            self.setter = self.bridge.lights[lamp_id]
            self.is_on = self.getter['state']['on']
            self.colour = self.getter['state']['xy']
            self.name = self.getter['name']
        except Exception:
            logger.exception('Failed to initialise Hue lamp %s', lamp_id)
            raise

    def __str__(self) -> str:
        if self.is_on:
            status = 'on and is set to xy:' + str(self.colour)
        else:
            status = 'off'
        return f'{self.name} is {status}'

    def turn_on(self) -> str:
        self.setter.state(on=True)
        return 'Lamp turned on'

    def turn_off(self) -> str:
        self.setter.state(on=False)
        return 'Lamp turned off'

    def set_colour(self, colour: tuple[float, float]) -> str:  # colour is a tuple of xy values
        try:
            self.setter.state(on=True, xy=colour)
            return 'Lamp changed colour'
        except Exception:
            logger.exception('Failed to set lamp colour to %s', colour)
            raise


def lookup_colour(temperature: int) -> str:
    # lookup table of temperatures to colours in database.sqlite3
    sql = 'WHERE temperature = (?)'
    what = (temperature,)  # tuple with single item
    results = get_rows('colours', 'hex_value', rows_sql=sql, args=what)
    if not results:
        raise ValueError(f'No colour found for temperature threshold {temperature}')
    return results[0][0]  # to return the hex value string only


def find_temp_threshold(temp: float) -> int:
    # find max and min thresholds from external database
    rows = get_rows('colours')

    all_thresholds = [row['temperature'] for row in rows]
    max_threshold = max(all_thresholds)
    min_threshold = min(all_thresholds)

    temp_threshold = int((temp + 15) / 5) * 5 - 15
    if temp_threshold > max_threshold:
        temp_threshold = max_threshold
    if temp_threshold < min_threshold:
        temp_threshold = min_threshold
    return temp_threshold


def convert_temp_to_colour(temp: float) -> tuple[float, float]:
    temp_threshold = find_temp_threshold(temp)
    converter = Converter(GamutA)
    colour = converter.hex_to_xy(lookup_colour(temp_threshold))
    return colour


def generate_graphs(timestamp: str) -> str:
    # observation sets
    now = datetime.strptime(timestamp, DATETIME_STRING)
    last_day = now - timedelta(days=1)
    last_week = now - timedelta(weeks=1)
    last_month = now - timedelta(weeks=4)
    observation_sets = {
        'last_day': last_day,
        'last_week': last_week,
        'last_month': last_month
    }

    # get datapoints from database
    colour_rows = get_rows('colours')
    hex_list = [f'#{row["hex_value"]}' for row in colour_rows]

    # graphs for every reading in last day, week, month
    for string, then in observation_sets.items():
        temps_count = {row['temperature']: 0 for row in colour_rows}

        # fetch data
        sql = 'WHERE timestamp BETWEEN datetime((?)) AND datetime((?))'
        when = (then, now)
        observation_rows = get_rows('observations', rows_sql=sql, args=when)

        # generate bar graph
        times = [row['timestamp'] for row in observation_rows]
        temps = [row['temperature'] for row in observation_rows]

        bar_chart = pygal.Bar(x_label_rotation=20,
                              x_labels_major_count=6,
                              show_minor_x_labels=False,
                              show_legend=False)
        bar_chart.add('Temperature', [
            {'value': temp,
             'color': '#' + lookup_colour(find_temp_threshold(temp))}
            for temp in temps]
                      )
        bar_chart.x_labels = times
        filename = string + '_bar.svg'
        try:
            bar_chart.render_to_file(FILEPATH + filename)
        except Exception:
            logger.exception('Failed to render bar chart %s', filename)
            raise

        # generate pie chart
        for temp in temps:
            temp_threshold = find_temp_threshold(temp)
            temps_count[temp_threshold] += 1
        custom_style = Style(colors=(tuple(hex_list)))
        pie_chart = pygal.Pie(inner_radius=0.6, style=custom_style)
        for temp, count in temps_count.items():
            pie_chart.add(str(temp), count)
        filename = string + '_pie.svg'
        try:
            pie_chart.render_to_file(FILEPATH + filename)
        except Exception:
            logger.exception('Failed to render pie chart %s', filename)
            raise

        # generate radar chart
        radar_chart = pygal.Radar(x_labels_major_count=12,
                                  show_minor_x_labels=False,
                                  show_legend=False)
        radar_chart.add('Temperature', [{'value': temp,
                                         'color': '#' + lookup_colour(find_temp_threshold(temp))}
                                        for temp in temps])
        radar_chart.x_labels = times
        filename = string + '_radar.svg'
        try:
            radar_chart.render_to_file(FILEPATH + filename)
        except Exception:
            logger.exception('Failed to render radar chart %s', filename)
            raise

    month_name = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct',
                  11: 'Nov', 12: 'Dec'}
    month_temps = {}
    month_colour = {}

    for i in range(12):
        # fetch data
        start = datetime.today() - relativedelta(months=(12 - i), day=1, hour=0, minute=0, second=0, microsecond=0)
        end = start + relativedelta(months=1)
        sql = 'WHERE timestamp BETWEEN datetime((?)) AND datetime((?))'
        when = (start, end)
        rows = get_rows('observations', rows_sql=sql, args=when)

        month_temps[start] = []
        month_temps[start].extend(row['temperature'] for row in rows)
        if month_temps[start]:
            month_colour[start] = '#' + lookup_colour(find_temp_threshold(mean(month_temps[start])))
        else:
            month_colour[start] = '#ffffff'

    # box plot of preceding 12 months
    custom_style = Style(
        background='transparent',
        plot_background='transparent',
        opacity='.6',
        opacity_hover='.9',
        transition='400ms ease-in',
        colors=([colour for month, colour in list(month_colour.items())]))

    box_plot = pygal.Box(legend_at_bottom=True,
                         legend_at_bottom_columns=12,
                         print_labels=True,
                         style=custom_style)
    for month_start, temps in month_temps.items():
        box_plot.add(month_name[month_start.month], temps)
    filename = 'annual_box.svg'
    try:
        box_plot.render_to_file(FILEPATH + filename)
    except Exception:
        logger.exception('Failed to render annual box chart %s', filename)
        raise

    return 'Created graphs'


hue_lamp_ids = {
    'den bloom': 10,
    'lounge bloom': 11
}


def weather() -> str:
    try:
        # Check current weather
        observation = WeatherObservation()
        observation.fetch(HOME_LOCATION)
        logger.info('%s', observation)

        # Set lounge bloom to current temperature
        lounge_bloom = HueLamp(hue_lamp_ids['lounge bloom'])
        if observation.temperature is None:
            raise RuntimeError('Observation temperature was not set')
        lounge_bloom.set_colour(convert_temp_to_colour(observation.temperature))
        # Set den bloom to current temperature
        den_bloom = HueLamp(hue_lamp_ids['den bloom'])
        den_bloom.set_colour(convert_temp_to_colour(observation.temperature))

        # Log weather observation
        observation.log()

        # generate new graphs
        if observation.timestamp is None:
            raise RuntimeError('Observation timestamp was not set')
        generate_graphs(observation.timestamp)

        return 'Fetched weather'
    except Exception:
        logger.exception('Weather job failed')
        return 'Weather job failed'


if __name__ == '__main__':
    weather()
