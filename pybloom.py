
'''
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
- Flask: framework for web site
- Jinja2: scripting language for Flask
- HTML5: basic structure of web site
- Bootstrap CSS: framework for CSS
- JavaScript: interactive features of web site
- Advanced Python Scheduler: periodic running of script

Notes:
- Program is intended to be called periodically
- Logged data is persistent
- Using free versions of all API, so there is limit to number of calls
'''

from datetime import datetime, timedelta
import qhue
from rgbxy import Converter
from rgbxy import GamutA
import pyowm
import pygal
from pygal.style import Style
from db_utils import db_connect, get_rows
import credentials

DATETIME_STRING = '%Y-%m-%d %H:%M:%S'
FILEPATH = './app/static/'
OWM_KEY = credentials.credentials['owm_key']
HUE_USERNAME = credentials.credentials['hue_username']
HUE_IP = credentials.credentials['hue_ip']
HOME_LOCATION = credentials.credentials['home_location']


class weather_observation:

    def __init__(self, timestamp=None, temperature=None, detailed_status=None):
        self.timestamp = timestamp,
        self.temperature = temperature,
        self.detailed_status = detailed_status

    def __str__(self):
        return f'Current weather: {self.detailed_status}, {self.temperature} celsius (made at {self.timestamp})'

    def new(self, location):  # expect e.g. 'London, GB'
        owm = pyowm.OWM(OWM_KEY)
        mgr = owm.weather_manager()
        weather = mgr.weather_at_place(location).weather
        self.timestamp = datetime.now().strftime(DATETIME_STRING)
        self.temperature = weather.temperature('celsius')['temp']
        self.detailed_status = weather.detailed_status
        return 'Fetched new observation'

    def log(self):
        # write to external database
        con = db_connect()
        cur = con.cursor()

        sql = '''INSERT INTO observations (timestamp,
                                           temperature,
                                           detailed_status)
                 VALUES (?, ?, ?)'''
        cur.execute(sql, (self.timestamp,
                          self.temperature,
                          self.detailed_status))
        con.commit()
        con.close()
        return 'Observation logged'

    def set(self, timestamp, temperature, detailed_status):  # for debug
        self.timestamp = timestamp
        self.temperature = temperature
        self.detailed_status = detailed_status
        return 'Observation set'


class hue_lamp:

    def __init__(self, lamp_id):
        # not accessible
        ip = HUE_IP
        username = HUE_USERNAME
        # accessible
        self.bridge = qhue.Bridge(ip, username)
        self.getter = self.bridge.lights[lamp_id]()
        self.setter = self.bridge.lights[lamp_id]
        self.is_on = self.getter['state']['on']
        self.colour = self.getter['state']['xy']
        self.name = self.getter['name']

    def __str__(self):
        if self.is_on:
            status = 'on and is set to xy:' + str(self.colour)
        else:
            status = 'off'
        return f'{self.name} is {status}'

    def turn_on(self):
        self.setter.state(on=True)
        return 'Lamp turned on'

    def turn_off(self):
        self.setter.state(on=False)
        return 'Lamp turned off'

    def set_colour(self, colour):  # colour is a tuple of xy values
        self.setter.state(on=True)
        self.setter.state(xy=colour)
        return 'Lamp changed colour'


def lookup_colour(temperature):
    # lookup table of temperatures to colours in database.sqlite3
    sql = 'WHERE temperature = (?)'
    what = (temperature, )  # tuple with single item
    results = get_rows('colours', 'hex_value', rows_sql=sql, args=what)
    return results[0][0]  # to return the hex value string only


def find_temp_threshold(temp):
    # find max and min thresholds from external database
    rows = get_rows('colours')

    all_thresholds = [row['temperature'] for row in rows]
    max_threshold = max(all_thresholds)
    min_threshold = min(all_thresholds)

    temp_threshold = int(temp/5) * 5
    if temp_threshold > max_threshold:
        temp_threshold = max_threshold
    if temp_threshold < min_threshold:
        temp_threshold = min_threshold
    return temp_threshold


def convert_temp_to_colour(temp):
    temp_threshold = find_temp_threshold(temp)
    converter = Converter(GamutA)
    colour = converter.hex_to_xy(lookup_colour(temp_threshold))
    return colour


def generate_graphs(timestamp):
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
    rows = get_rows('colours')
    hex_list = [f'#{hex}' for hex in [row['hex_value'] for row in rows]]
    temps_count = {row['temperature']: 0 for row in rows}

    # 3x graphs for every reading in last day, week, month
    for string, then in observation_sets.items():
        # fetch data
        sql = 'WHERE timestamp BETWEEN datetime((?)) AND datetime((?))'
        when = (then, now)
        rows = get_rows('observations', rows_sql=sql, args=when)

        # generate bar graph
        times = [row['timestamp'] for row in rows]
        temps = [row['temperature'] for row in rows]

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
        bar_chart.render_to_file(FILEPATH + filename)

        # generate pie chart
        for temp in temps:
            temp_threshold = find_temp_threshold(temp)
            temps_count[temp_threshold] += 1
        custom_style = Style(colors=(tuple(hex_list)))
        pie_chart = pygal.Pie(inner_radius=0.6, style=custom_style)
        for temp, count in temps_count.items():
            pie_chart.add(str(temp), count)
        filename = string + '_pie.svg'
        pie_chart.render_to_file(FILEPATH + filename)

    return 'Created graphs'


hue_lamp_ids = {
    'den bloom': 10,
    'lounge bloom': 11
}


def weather():
    # Check current weather
    observation = weather_observation()
    observation.new(HOME_LOCATION)
    # observation.set(datetime.now().strftime(DATETIME_STRING), 23, 'dummy observation')
    print(observation)

    # Set lounge bloom to current temperature
    lounge_bloom = hue_lamp(hue_lamp_ids['lounge bloom'])
    lounge_bloom.set_colour(convert_temp_to_colour(observation.temperature))
    # Set den bloom to current temperature
    den_bloom = hue_lamp(hue_lamp_ids['den bloom'])
    den_bloom.set_colour(convert_temp_to_colour(observation.temperature))

    # Log weather observation
    observation.log()

    # generate new graphs
    generate_graphs(observation.timestamp)

    return 'Fetched weather'


weather()
