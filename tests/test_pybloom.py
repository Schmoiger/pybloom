import os
import sys

import pytest


CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
PARENT_DIR = os.path.dirname(CURRENT_DIR)
sys.path.append(PARENT_DIR)

import db_utils
import pybloom


def test_find_temp_threshold_clamps_to_database_bounds(monkeypatch):
    monkeypatch.setattr(
        pybloom,
        'get_rows',
        lambda table, columns='*', **kwargs: [
            {'temperature': -15},
            {'temperature': 0},
            {'temperature': 5},
            {'temperature': 10},
            {'temperature': 15},
            {'temperature': 20},
            {'temperature': 25},
            {'temperature': 30},
            {'temperature': 35},
            {'temperature': 40},
        ],
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
