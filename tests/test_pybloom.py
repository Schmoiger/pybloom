import pytest
import sqlite3

import db_utils
import pybloom


def test_find_temp_threshold_clamps_to_database_bounds(monkeypatch, colour_threshold_rows):
    monkeypatch.setattr(
        pybloom,
        'get_rows',
        lambda table, columns='*', **kwargs: colour_threshold_rows,
    )

    assert pybloom.find_temp_threshold(-99) == -15
    assert pybloom.find_temp_threshold(999) == 40


def test_lookup_colour_returns_matching_hex(monkeypatch):
    monkeypatch.setattr(
        pybloom,
        'get_rows',
        lambda table, columns='*', **kwargs: [{'hex_value': 'ffbf00'}],
    )

    assert pybloom.lookup_colour(25) == 'ffbf00'


def test_lookup_colour_raises_for_missing_threshold(monkeypatch):
    monkeypatch.setattr(pybloom, 'get_rows', lambda table, columns='*', **kwargs: [])

    with pytest.raises(ValueError, match='No colour found for temperature threshold 123'):
        pybloom.lookup_colour(123)


def test_weather_observation_set_and_str():
    observation = pybloom.WeatherObservation()
    observation.set('2026-06-12 10:00:00', 21.5, 'clear sky')

    assert observation.timestamp == '2026-06-12 10:00:00'
    assert observation.temperature == 21.5
    assert observation.detailed_status == 'clear sky'
    assert str(observation) == 'Current weather: clear sky, 21.5 celsius (made at 2026-06-12 10:00:00)'


def test_get_rows_rejects_invalid_table():
    with pytest.raises(ValueError, match='invalid table name'):
        db_utils.get_rows('not_a_table')


def test_init_db_creates_and_seeds_schema(tmp_path):
    db_path = tmp_path / 'database.sqlite3'
    db_utils.init_db(str(db_path))

    con = db_utils.db_connect(str(db_path))
    try:
        cur = con.cursor()
        cur.execute('SELECT COUNT(*) FROM colours')
        assert cur.fetchone()[0] == 12
        cur.execute('SELECT COUNT(*) FROM observations')
        assert cur.fetchone()[0] == 0
    finally:
        con.close()


def test_get_rows_returns_named_rows(tmp_path, monkeypatch):
    db_path = tmp_path / 'database.sqlite3'
    db_utils.init_db(str(db_path))

    con = sqlite3.connect(str(db_path))
    try:
        con.execute(
            "INSERT INTO observations (timestamp, temperature, detailed_status) VALUES (?, ?, ?)",
            ('2026-06-12 10:00:00', 21.5, 'clear sky'),
        )
        con.commit()
    finally:
        con.close()

    monkeypatch.setattr(db_utils, 'db_connect', lambda db_file=db_utils.DEFAULT_DB: sqlite3.connect(str(db_path)))

    rows = db_utils.get_rows('observations')

    assert rows[0]['timestamp'] == '2026-06-12 10:00:00'
    assert rows[0]['temperature'] == 21.5
    assert rows[0]['detailed_status'] == 'clear sky'


def test_weather_orchestration_calls_external_steps(monkeypatch, mock_owm, mock_hue):
    fetched = []
    logged = []
    generated = []

    def fake_fetch(self, location):
        fetched.append(location)
        self.timestamp = '2026-06-12 10:00:00'
        self.temperature = 21.5
        self.detailed_status = 'clear sky'
        return 'Fetched new observation'

    def fake_log(self):
        logged.append((self.timestamp, self.temperature, self.detailed_status))
        return 'Observation logged'

    def fake_generate(timestamp):
        generated.append(timestamp)
        return 'Created graphs'

    monkeypatch.setattr(pybloom.WeatherObservation, 'fetch', fake_fetch)
    monkeypatch.setattr(pybloom.WeatherObservation, 'log', fake_log)
    monkeypatch.setattr(pybloom, 'generate_graphs', fake_generate)
    monkeypatch.setattr(pybloom, 'convert_temp_to_colour', lambda temp: (0.1, 0.2))

    result = pybloom.weather()

    assert result == 'Fetched weather'
    assert fetched == [pybloom.HOME_LOCATION]
    assert logged == [('2026-06-12 10:00:00', 21.5, 'clear sky')]
    assert generated == ['2026-06-12 10:00:00']


def test_hue_lamp_set_colour_combines_state_updates(mock_hue):
    lamp = pybloom.HueLamp(10)
    lamp.set_colour((0.1, 0.2))

    assert lamp.setter.calls[-1] == {'on': True, 'xy': (0.1, 0.2)}


def test_home_route_renders(flask_client):
    response = flask_client.get('/')

    assert response.status_code == 200
    assert b'Latest data' in response.data
    assert b'Temperatures over Last Year' in response.data


def test_colours_route_renders(flask_client):
    response = flask_client.get('/colours')

    assert response.status_code == 200
    assert b'Colour key' in response.data
