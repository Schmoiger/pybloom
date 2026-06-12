import ast
import sqlite3
import types
import sys
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

if not hasattr(ast, 'Str'):
    class _CompatStr(ast.AST):
        _fields = ('s',)

        def __init__(self, s=''):
            self.s = s

    ast.Str = _CompatStr

if 'qhue' not in sys.modules:
    qhue_stub = types.ModuleType('qhue')

    class _Bridge:
        def __init__(self, *args, **kwargs):
            self.lights = {}

    qhue_stub.Bridge = _Bridge
    sys.modules['qhue'] = qhue_stub

if 'pyowm' not in sys.modules:
    pyowm_stub = types.ModuleType('pyowm')

    class _OWM:
        def __init__(self, *args, **kwargs):
            pass

        def weather_manager(self):
            raise RuntimeError('pyowm stub should be monkeypatched in tests')

    pyowm_stub.OWM = _OWM
    sys.modules['pyowm'] = pyowm_stub

if 'pygal' not in sys.modules:
    pygal_stub = types.ModuleType('pygal')

    class _Chart:
        def __init__(self, *args, **kwargs):
            self.series = []
            self.x_labels = []

        def add(self, *args, **kwargs):
            self.series.append((args, kwargs))

        def render_to_file(self, *args, **kwargs):
            return None

    class _Style:
        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs

    pygal_stub.Bar = _Chart
    pygal_stub.Pie = _Chart
    pygal_stub.Radar = _Chart
    pygal_stub.Box = _Chart
    pygal_style_stub = types.ModuleType('pygal.style')
    pygal_style_stub.Style = _Style
    sys.modules['pygal'] = pygal_stub
    sys.modules['pygal.style'] = pygal_style_stub

import db_utils


@pytest.fixture
def temp_db(tmp_path):
    """Create a temporary SQLite database with the PyBloom schema."""
    db_path = tmp_path / 'database.sqlite3'
    con = None
    try:
        db_utils.init_db(str(db_path))
        con = db_utils.db_connect(str(db_path))
        con.row_factory = sqlite3.Row
        yield con
    finally:
        if con is not None:
            con.close()


@pytest.fixture
def colour_threshold_rows():
    """Return the seeded colour thresholds used by the app."""
    return [
        {'temperature': -15, 'hex_value': '0040ff'},
        {'temperature': -10, 'hex_value': '0080ff'},
        {'temperature': -5, 'hex_value': '00bfff'},
        {'temperature': 0, 'hex_value': '00ffff'},
        {'temperature': 5, 'hex_value': '00ffbf'},
        {'temperature': 10, 'hex_value': '00ff80'},
        {'temperature': 15, 'hex_value': 'bfff00'},
        {'temperature': 20, 'hex_value': 'ffff00'},
        {'temperature': 25, 'hex_value': 'ffbf00'},
        {'temperature': 30, 'hex_value': 'ff8000'},
        {'temperature': 35, 'hex_value': 'ff4000'},
        {'temperature': 40, 'hex_value': 'ff0000'},
    ]


@pytest.fixture
def sample_observations():
    """Return a small observation set for logic tests."""
    return [
        {'timestamp': '2026-06-12 09:00:00', 'temperature': 18.5},
        {'timestamp': '2026-06-12 10:00:00', 'temperature': 21.0},
    ]


@pytest.fixture
def temp_svg_dir(tmp_path):
    """Provide a temporary output directory for SVG generation tests."""
    return tmp_path / 'svg'


@pytest.fixture
def flask_client():
    """Return a Flask test client for route-level tests."""
    from app import app

    return app.test_client()


@pytest.fixture
def mock_owm(monkeypatch):
    """Stub the weather API client used by `WeatherObservation.fetch()`."""
    import pybloom

    class FakeWeather:
        detailed_status = 'clear sky'

        @staticmethod
        def temperature(unit):
            return {'temp': 21.5}

    class FakeWeatherAtPlace:
        weather = FakeWeather()

    class FakeWeatherManager:
        @staticmethod
        def weather_at_place(location):
            return FakeWeatherAtPlace()

    class FakeOWM:
        @staticmethod
        def weather_manager():
            return FakeWeatherManager()

    monkeypatch.setattr(pybloom.pyowm, 'OWM', lambda api_key: FakeOWM())


@pytest.fixture
def mock_hue(monkeypatch):
    """Stub the Hue bridge used by `HueLamp`."""
    import pybloom

    class FakeLights:
        def __getitem__(self, lamp_id):
            class FakeLight:
                def __init__(self):
                    self.calls = []

                def __call__(self):
                    return {
                        'state': {'on': False, 'xy': [0.0, 0.0]},
                        'name': f'Lamp {lamp_id}',
                    }

                def state(self, **kwargs):
                    self.calls.append(kwargs)

            return FakeLight()

    class FakeBridge:
        def __init__(self, ip, username):
            self.lights = FakeLights()

    monkeypatch.setattr(pybloom.qhue, 'Bridge', FakeBridge)
