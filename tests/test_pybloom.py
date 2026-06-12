import pytest

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


def test_home_route_renders(flask_client):
    response = flask_client.get('/')

    assert response.status_code == 200


def test_colours_route_renders(flask_client):
    response = flask_client.get('/colours')

    assert response.status_code == 200
