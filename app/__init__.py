import logging
import ast
import sys
import types
import ssl
import queue as stdlib_queue
from http import client as http_client

if not hasattr(ast, 'Str'):
    class _CompatStr(ast.Constant):
        _fields = ('s',)
        _field_types = {'s': str}
        _attributes = ('lineno', 'col_offset', 'end_lineno', 'end_col_offset')

        def __new__(cls, s=''):
            return ast.Constant.__new__(cls, s)

        def __init__(self, s=''):
            ast.Constant.__init__(self, s)

        @property
        def s(self):
            return self.value

        @s.setter
        def s(self, value):
            self.value = value

    ast.Str = _CompatStr

if 'pkg_resources' not in sys.modules:
    pkg_resources_stub = types.ModuleType('pkg_resources')

    class DistributionNotFound(Exception):
        pass

    def get_distribution(name):
        raise DistributionNotFound(name)

    def iter_entry_points(group, name=None):
        return iter(())

    pkg_resources_stub.DistributionNotFound = DistributionNotFound
    pkg_resources_stub.get_distribution = get_distribution
    pkg_resources_stub.iter_entry_points = iter_entry_points
    sys.modules['pkg_resources'] = pkg_resources_stub

if 'urllib3.packages.six.moves.http_client' not in sys.modules:
    packages_mod = sys.modules.setdefault('urllib3.packages', types.ModuleType('urllib3.packages'))
    packages_mod.__path__ = []
    six_mod = sys.modules.setdefault('urllib3.packages.six', types.ModuleType('urllib3.packages.six'))
    six_mod.__path__ = []
    moves_mod = sys.modules.setdefault('urllib3.packages.six.moves', types.ModuleType('urllib3.packages.six.moves'))
    moves_mod.__path__ = []
    http_client_mod = types.ModuleType('urllib3.packages.six.moves.http_client')
    http_client_mod.IncompleteRead = http_client.IncompleteRead
    http_client_mod.HTTPConnection = http_client.HTTPConnection
    http_client_mod.HTTPResponse = http_client.HTTPResponse
    http_client_mod.HTTPException = http_client.HTTPException
    moves_mod.http_client = http_client_mod
    six_mod.moves = moves_mod
    packages_mod.six = six_mod
    sys.modules['urllib3.packages.six.moves.http_client'] = http_client_mod
    queue_mod = types.ModuleType('urllib3.packages.six.moves.queue')
    queue_mod.Queue = stdlib_queue.Queue
    queue_mod.LifoQueue = stdlib_queue.LifoQueue
    queue_mod.PriorityQueue = stdlib_queue.PriorityQueue
    queue_mod.Empty = stdlib_queue.Empty
    queue_mod.Full = stdlib_queue.Full
    moves_mod.queue = queue_mod
    sys.modules['urllib3.packages.six.moves.queue'] = queue_mod

if 'urllib3.packages.ssl_match_hostname' not in sys.modules:
    ssl_match_hostname_mod = types.ModuleType('urllib3.packages.ssl_match_hostname')
    ssl_match_hostname_mod.CertificateError = ssl.SSLCertVerificationError

    def match_hostname(cert, hostname):
        return ssl.match_hostname(cert, hostname)

    ssl_match_hostname_mod.match_hostname = match_hostname
    sys.modules['urllib3.packages.ssl_match_hostname'] = ssl_match_hostname_mod

from flask import Flask
app = Flask(__name__)
from db_utils import init_db

init_db()

logging.basicConfig(level=logging.INFO)

from app import routes
from apscheduler.schedulers.background import BackgroundScheduler


schedule = BackgroundScheduler(daemon=True)


@app.before_first_request
def start_scheduler():
    from datetime import datetime
    from pybloom import weather

    schedule.add_job(lambda: weather(), 'interval', minutes=10, next_run_time=datetime.now())
    schedule.start()
