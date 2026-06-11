# Codebase Improvement Review

Senior solution architect review of the PyBloom codebase, covering **solution architecture**, **code quality**, and **test quality**.

---

## 1. Solution Architecture

### 1.1 Module-level side effects in `db_utils.py` (Critical)

**File:** `db_utils.py`, lines 41–83

Database connection, table creation, and seed data insertion all execute at import time — there is no `if __name__ == '__main__':` guard. Every time any module imports `db_utils` (including tests, linting tools, and IDE introspection), it connects to the database and runs DDL. This causes:

- Unexpected database file creation in the working directory
- Test isolation failures — tests inadvertently modify the production database
- Import-time errors if the database path is not writable

**Recommendation:** Move all schema creation and seed logic into an explicit `init_db()` function. Call it from the application startup path, not at import time.

---

### 1.2 Monolithic `pybloom.py` — no separation of concerns

**File:** `pybloom.py` (292 lines)

This single file contains five distinct responsibilities:

| Responsibility | Lines |
|---|---|
| Weather observation fetching (OWM API) | `WeatherObservation` class |
| Hue lamp control (Philips Hue API) | `HueLamp` class |
| Temperature-to-colour conversion | `lookup_colour()`, `find_temp_threshold()`, `convert_temp_to_colour()` |
| Graph generation (pygal) | `generate_graphs()` (100+ lines) |
| Orchestration / scheduling | `weather()` function |

**Recommendation:** Split into dedicated modules:
- `weather.py` — weather observation fetching
- `hue.py` — Hue lamp control
- `colours.py` — temperature-to-colour mapping
- `graphs.py` — graph generation
- `scheduler.py` — orchestration and scheduling

This improves testability, readability, and allows independent evolution of each concern.

---

### 1.3 No dependency injection — untestable classes

**Files:** `pybloom.py`, `WeatherObservation.__init__()` and `new()`, `HueLamp.__init__()`

Both classes create their own external dependencies internally:

```python
# WeatherObservation.new() creates a new OWM instance every call
owm = pyowm.OWM(OWM_KEY)

# HueLamp.__init__() makes network calls in the constructor
self.bridge = qhue.Bridge(ip, username)
self.getter = self.bridge.lights[lamp_id]()  # HTTP request!
```

This makes unit testing impossible without patching at the module level. The constructor of `HueLamp` makes a live HTTP call to the Hue bridge, which will fail in any test or CI environment.

**Recommendation:** Accept dependencies as constructor parameters (dependency injection). For example:
- `WeatherObservation(owm_api_key=..., db_connection=...)`
- `HueLamp(bridge=None, lamp_id=...)` where `bridge` can be a mock

---

### 1.4 Hardcoded configuration — no environment variable support

**File:** `pybloom.py`, lines 44–47

```python
OWM_KEY = credentials.credentials['owm_key']
HUE_USERNAME = credentials.credentials['hue_username']
HUE_IP = credentials.credentials['hue_ip']
HOME_LOCATION = credentials.credentials['home_location']
```

Configuration is loaded from a Python file (`credentials.py`) at module import time. There is no support for environment variables, `.env` files, or Flask configuration objects. This creates several problems:

- Secrets are loaded as Python code (security risk if the file is compromised)
- No way to override configuration per environment (dev/staging/prod)
- No validation of required configuration values
- The `credentials.py` file is gitignored, so there's no documentation of what keys are required

**Recommendation:**
- Use environment variables with `os.environ.get()` and a `.env` file (via `python-dotenv`)
- Add a configuration schema with validation at startup
- Document required variables in `.env.example`

---

### 1.5 Tight coupling between Flask app and scheduler

**File:** `app/__init__.py`

```python
from app import routes
from pybloom import weather

schedule = BackgroundScheduler(daemon=True)
schedule.add_job(lambda: weather(), 'interval', minutes=10)
schedule.start()
```

The scheduler starts at import time of the Flask app. This means:
- It starts during testing, causing side effects
- There's no way to start the scheduler independently
- There's no graceful shutdown — the daemon thread is killed when the process exits
- No configuration of the interval (hardcoded to 10 minutes)

**Recommendation:**
- Move scheduler setup into a dedicated factory function
- Add configuration for the interval
- Register a shutdown hook with `atexit` or Flask's teardown
- Only start the scheduler in the actual application, not during imports

---

### 1.6 No error handling anywhere

**Files:** All Python files

There are zero `try`/`except` blocks in the entire codebase. Any failure — network timeout from OWM, Hue bridge unreachable, database locked, invalid API response — will crash the scheduler job silently and stop all future weather updates.

**Recommendation:**
- Add error handling around all external API calls (OWM, Hue bridge)
- Add error handling around database operations
- Implement retry logic with exponential backoff for transient failures
- Log errors rather than crashing silently
- Consider a circuit breaker pattern for the Hue bridge connection

---

### 1.7 No logging — uses `print()` statements

**File:** `pybloom.py`, line 273

```python
print(observation)
```

The application uses `print()` for output. There is no structured logging, no log levels, no log rotation, and no way to filter or redirect output.

**Recommendation:**
- Use Python's `logging` module with configurable log levels
- Add structured logging with timestamps, log levels, and context
- Configure different handlers for console and file output
- Log weather observations, Hue commands, graph generation, and errors

---

### 1.8 Synchronous graph generation blocks the scheduler

**File:** `pybloom.py`, `generate_graphs()` (lines 158–260)

Graph generation is CPU-intensive (multiple chart types, file I/O) and runs synchronously within the scheduler job. This blocks the scheduler thread and could cause missed jobs if generation takes longer than the interval.

Additionally, `generate_graphs()` regenerates ALL graphs (last day, last week, last month, annual) every 10 minutes, even though only the "last day" graph needs updating each cycle.

**Recommendation:**
- Move graph generation to a separate thread or process
- Only regenerate graphs that have changed since the last observation
- Consider caching strategies for the annual box plot

---

### 1.9 No database connection management pattern

**Files:** `db_utils.py`, `pybloom.py`

Every database operation creates a new connection, opens a cursor, executes, and closes. There is no connection pooling, no context manager for automatic cleanup, and no handling of concurrent access (SQLite supports one writer at a time).

```python
# In WeatherObservation.log()
con = db_connect()
cur = con.cursor()
cur.execute(sql, ...)
con.commit()
con.close()
```

If an exception occurs between `connect()` and `close()`, the connection leaks.

**Recommendation:**
- Use a context manager pattern for database connections
- Consider using `contextlib.contextmanager` for `db_connect()`
- Add WAL mode to the database for better concurrent read/write performance
- Consider using a connection pool if the application grows

---

### 1.10 No database migration strategy

**File:** `db_utils.py`

The schema is created with `CREATE TABLE IF NOT EXISTS` at import time. If the schema ever changes (adding columns, modifying constraints), there's no migration path. Existing databases would not be updated.

**Recommendation:**
- Use a migration tool (e.g., `Alembic` for SQLite, or a simple versioned migration script)
- Add a schema version table to track applied migrations

---

### 1.11 Static content computed at import time never updates

**File:** `app/routes.py`, lines 6–7

```python
CONTENT = content.graphs()
COLOURS_TABLE = content.colours_table()
```

These are computed once when the module is imported. The web page will always show the same graph file paths and the same colour table, even as new data arrives. The graph file paths are static (hardcoded in `content.graphs()`), so they don't actually need recomputing, but `COLOURS_TABLE` would never reflect database changes.

**Recommendation:**
- Move dynamic data fetching into the route handlers
- Use `@app.before_request` or a template context processor for data that changes
- Keep static configuration separate from dynamic data

---

### 1.12 `requirements.txt` and `pyproject.toml` duplication

**Files:** `requirements.txt`, `pyproject.toml`

Both files list all dependencies with pinned versions. They can easily get out of sync. Since the project uses `uv` (which reads from `pyproject.toml`), the `requirements.txt` is redundant.

**Recommendation:**
- Remove `requirements.txt` and rely solely on `pyproject.toml`
- Use `uv pip compile` to generate a lockfile if a flat requirements file is needed for deployment

---

### 1.13 No health checks or observability

There is no way to know:
- Whether the scheduler is running and executing jobs
- When the last successful weather observation was fetched
- Whether the Hue bridge is reachable
- Whether the database is healthy

**Recommendation:**
- Add a `/health` endpoint that reports scheduler status, last observation time, and connectivity
- Add metrics collection for key operations

---

## 2. Code Quality

### 2.1 Critical bug: trailing commas create tuples in `WeatherObservation.__init__`

**File:** `pybloom.py`, lines 52–55

```python
def __init__(self, timestamp=None, temperature=None, detailed_status=None):
    self.timestamp = timestamp,   # BUG: creates tuple (None,), not None
    self.temperature = temperature,   # BUG: creates tuple (None,), not None
    self.detailed_status = detailed_status
```

The trailing commas after `timestamp` and `temperature` cause Python to create single-element tuples instead of assigning the values directly. `self.timestamp` becomes `(None,)` rather than `None`. This affects:
- The `__str__` method output (tuples display with parentheses)
- Database insertion (tuples are inserted instead of strings/floats)
- String formatting throughout the application

**Fix:** Remove the trailing commas.

---

### 2.2 Critical bug: `get_rows()` error path continues to execute

**File:** `db_utils.py`, lines 30–38

```python
if rows_sql.count('?') != len(args):
    results = 'Unexpected number of arguments in row modifier'

cur.execute('SELECT ' + columns + ' FROM ' + table + rows_sql, args)
results = cur.fetchall()
```

When the argument count mismatch is detected, `results` is set to an error string, but execution continues to `cur.execute()` anyway — the error is never raised. Additionally, if the table name is invalid, `con` is never assigned (line 19 is inside the `if` block), so `con.close()` on line 37 will raise a `NameError`.

**Fix:** Add a `raise` or `return` after the error detection. Use `try`/`except` or restructure the control flow.

---

### 2.3 Critical bug: `temps_count` accumulates across observation sets

**File:** `pybloom.py`, lines 173, 200–208

```python
temps_count = {row['temperature']: 0 for row in rows}  # initialized once

for string, then in observation_sets.items():
    # ...
    for temp in temps:
        temp_threshold = find_temp_threshold(temp)
        temps_count[temp_threshold] += 1  # accumulates across iterations!
```

The `temps_count` dictionary is initialized once before the loop, but is never reset between iterations. The pie chart for "last week" includes counts from "last day", and "last month" includes counts from both. Each pie chart should only reflect its own time period.

**Fix:** Reset `temps_count` at the start of each loop iteration.

---

### 2.4 Critical bug: `colours.html` uses tuple indexing on `sqlite3.Row`

**File:** `app/templates/colours.html`, lines 14–15

```html
<td>{{row[1]}}</td>
<td id="{{row[2]}}">{{row[2]}}</td>
```

The `get_rows()` function sets `con.row_factory = sqlite3.Row`, which returns Row objects that support both index and key access. However, `row[1]` and `row[2]` assume a specific column ordering (id=0, temperature=1, hex_value=2). If the schema changes, this silently breaks. Using `row['temperature']` and `row['hex_value']` would be more robust and readable.

---

### 2.5 `lookup_colour()` assumes results exist — no bounds checking

**File:** `pybloom.py`, lines 127–132

```python
def lookup_colour(temperature):
    sql = 'WHERE temperature = (?)'
    what = (temperature,)
    results = get_rows('colours', 'hex_value', rows_sql=sql, args=what)
    return results[0][0]
```

If no row matches the temperature (e.g., due to a data issue), `results` is an empty list and `results[0]` raises an `IndexError`. There's no validation or error handling.

---

### 2.6 `find_temp_threshold()` recalculates static data on every call

**File:** `pybloom.py`, lines 135–148

Every call to `find_temp_threshold()` queries the database to get all colour thresholds. These thresholds are static seed data that never changes after initialization. In `generate_graphs()`, this function is called once per temperature reading, resulting in dozens of redundant database queries per graph generation cycle.

**Recommendation:** Cache the thresholds in a module-level variable or pass them as a parameter.

---

### 2.7 `generate_graphs()` imports inside function body

**File:** `pybloom.py`, lines 222–223

```python
from statistics import mean
from dateutil.relativedelta import relativedelta
```

These imports should be at the top of the file per PEP 8. Importing inside a function is generally only done to avoid circular imports, which is not the case here.

---

### 2.8 `HueLamp.set_colour()` makes two API calls instead of one

**File:** `pybloom.py`, lines 121–124

```python
def set_colour(self, colour):
    self.setter.state(on=True)      # API call 1
    self.setter.state(xy=colour)    # API call 2
```

The Hue API supports setting `on` and `xy` in a single PUT request. Making two calls doubles the network latency and creates a brief moment where the lamp is on but not yet the right colour.

**Fix:** `self.setter.state(on=True, xy=colour)`

---

### 2.9 No type hints anywhere

**Files:** All Python files

There are no type annotations on any function signatures, class attributes, or return types. This makes the code harder to understand, prevents IDE auto-completion, and allows type errors to go undetected.

**Recommendation:** Add type hints to all public functions and classes. Use `mypy` for static type checking.

---

### 2.10 No docstrings on functions or classes

**Files:** `pybloom.py`, `db_utils.py`, `app/content.py`

The module-level docstring in `pybloom.py` is a design document, not a standard Python docstring. No functions or classes have docstrings explaining their purpose, parameters, return values, or exceptions.

---

### 2.11 No input validation

**Files:** All Python files

There is no validation of:
- Temperature values from the OWM API
- API response structure
- Database query results
- User input (though there is minimal user input)

A malformed API response could cause silent data corruption.

---

### 2.12 `WeatherObservation.new()` is an anti-pattern

**File:** `pybloom.py`, lines 60–67

The `new()` method mutates the object's attributes and returns a status string. This is not a constructor or factory method — it's a mutation method with a misleading name. The method name `new` suggests creating a new instance, but it actually modifies the existing one.

**Recommendation:** Rename to `fetch()` or `update()`, or make it a `@classmethod` factory that returns a new instance.

---

### 2.13 `set()` method in production code

**File:** `pybloom.py`, lines 85–89

```python
def set(self, timestamp, temperature, detailed_status):  # for debug
```

Debug-only methods should not be in production code. Use a test fixture or factory method instead.

---

### 2.14 Duplicate dependency declarations

**Files:** `pyproject.toml`, `requirements.txt`

Both files declare all dependencies. The `pyproject.toml` includes transitive dependencies (like `certifi`, `idna`, `urllib3`) that should not be declared directly — they should be resolved automatically by the package manager.

**Recommendation:** In `pyproject.toml`, only declare direct dependencies. Let `uv` (or `pip`) resolve transitive dependencies and pin them in the lockfile.

---

### 2.15 `pyproject.toml` placeholder description

**File:** `pyproject.toml`, line 4

```toml
description = "Add your description here"
```

Should be updated to: `"Indicate the outside temperature on Philips Hue lights."`

---

### 2.16 `base.html` references non-existent `brand.svg`

**File:** `app/templates/base.html`, line 32

```html
<img src="{{ url_for('static', filename='brand.svg') }}" ...>
```

The `brand.svg` file does not exist in `app/static/`. Only `favicon.ico`, `favicon_old.ico`, `MindRocketLogo.jpg`, and `MindRocketLogo.png` exist. This causes a 404 error on every page load.

---

### 2.17 `base.html` uses Bootstrap 5.0.0-alpha2

**File:** `app/templates/base.html`, lines 15, 67

Bootstrap 5.0.0-alpha2 is an old pre-release version. The current stable release is Bootstrap 5.3.x. Alpha versions may have breaking changes, removed features, and security issues.

---

### 2.18 `base.html` has HTML attribute error

**File:** `app/templates/base.html`, line 37

```html
<button ... aria-expanded"false">
```

Missing `=` sign. Should be `aria-expanded="false"`.

---

### 2.19 `index.html` has incorrect alt text

**File:** `app/templates/index.html`, lines 11–13

All four `<img>` tags use `alt="Temperature over last week"` regardless of which time period they represent.

---

### 2.20 No `__repr__` methods

**Files:** `pybloom.py`

Only `__str__` is defined. Adding `__repr__` would improve debugging output in the REPL and log messages.

---

### 2.21 `WeatherObservation` and `HueLamp` don't follow Python naming conventions

**File:** `pybloom.py`

The class names follow PascalCase correctly, but the manual (`docs/PyBloom_manual.md`) refers to them as `weather_observation` and `hue_lamp` (snake_case). The code and documentation should be consistent.

---

### 2.22 `get_rows()` SQL injection surface

**File:** `db_utils.py`, line 33

```python
cur.execute('SELECT ' + columns + ' FROM ' + table + rows_sql, args)
```

The `table` and `columns` parameters are concatenated directly into the SQL string. While `rows_sql` uses parameterized queries (safe), the table and column names are not sanitized. If user input ever reaches these parameters, it would be an SQL injection vulnerability.

**Recommendation:** Validate `table` and `columns` against an allowlist, or use `sqlite3` PRAGMA to query the schema.

---

## 3. Test Quality

### 3.1 No tests exist

**File:** `tests/test.py`

This file contains **zero test functions**. It is not a test suite — it is a script that:
1. Imports functions from `pybloom`
2. Queries the production database
3. Generates a single SVG file
4. Contains commented-out code

There are no assertions, no test framework, no test runner configuration, and no test isolation.

---

### 3.2 No test framework

There is no `pytest`, `unittest`, or any test framework in the dependencies. The `pyproject.toml` has no `[project.optional-dependencies]` for dev/test dependencies.

**Recommendation:** Add `pytest` as a dev dependency. Add a `[project.optional-dependencies]` section:
```toml
[project.optional-dependencies]
dev = ["pytest", "pytest-cov", "pytest-mock", "responses"]
```

---

### 3.3 `sys.path` hack instead of proper package structure

**File:** `tests/test.py`, lines 4–8

```python
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
```

This is a well-known anti-pattern. The project should be structured as an installable package so that imports work naturally.

**Recommendation:** Install the project in development mode (`pip install -e .`) so imports resolve correctly without path manipulation.

---

### 3.4 Tests use the production database

**File:** `tests/test.py`, line 16

```python
rows = db_utils.get_rows('observations')
```

Tests query the real `database.sqlite3` file. This means:
- Tests require a populated database to run
- Tests can corrupt production data
- Tests are not reproducible (results depend on what observations exist)
- Tests cannot run in CI

**Recommendation:**
- Use an in-memory SQLite database for tests (`:memory:`)
- Create test fixtures with known data
- Use a conftest.py to set up and tear down test databases

---

### 3.5 No mocking of external services

The codebase makes HTTP calls to two external services:
- Open Weather Map API (weather data)
- Philips Hue Bridge (light control)

There are no tests that mock these services, so:
- Tests require live API keys and network access
- Tests require a real Hue bridge on the network
- Tests can trigger real API usage (consuming free tier quotas)
- Tests can physically change light colours in someone's home

**Recommendation:** Use `responses` (for `requests` mocking) or `pytest-mock` to mock all external HTTP calls.

---

### 3.6 No test coverage measurement

There is no `pytest-cov` or `coverage` configuration. No way to know what percentage of code is tested.

**Recommendation:** Add `pytest-cov` and configure minimum coverage thresholds:
```toml
[tool.pytest.ini_options]
addopts = "--cov=app --cov=pybloom --cov=db_utils --cov-report=term-missing --cov-fail-under=80"
```

---

### 3.7 No test configuration

There is no `pytest.ini`, `conftest.py`, `setup.cfg`, or `[tool.pytest.ini_options]` in `pyproject.toml`.

**Recommendation:** Add pytest configuration to `pyproject.toml`:
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_functions = ["test_*"]
```

---

### 3.8 What tests should exist

For a project of this nature, the following test categories are needed:

#### Unit Tests
- `test_colours.py` — test `find_temp_threshold()`, `lookup_colour()`, `convert_temp_to_colour()` with known inputs and expected outputs
- `test_weather.py` — test `WeatherObservation` class with mocked OWM API
- `test_hue.py` — test `HueLamp` class with mocked Hue bridge
- `test_db_utils.py` — test `get_rows()` and `db_connect()` with in-memory database
- `test_graphs.py` — test `generate_graphs()` produces valid SVG files

#### Integration Tests
- `test_routes.py` — test Flask routes return correct status codes and content
- `test_scheduler.py` — test that the scheduler starts and executes jobs

#### Edge Cases
- Temperature at exact threshold boundaries
- Empty database (no observations)
- API returning unexpected data formats
- Database connection failures
- Hue bridge unreachable

---

### 3.9 No CI/CD pipeline

There is no `.github/workflows/`, no GitHub Actions configuration, no pre-commit hooks, and no automated testing.

**Recommendation:** Add a basic CI pipeline:
```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
      - run: uv sync --dev
      - run: uv run pytest
```

---

## 4. Summary of Priorities

### Must Fix (Bugs)

| # | Issue | File | Severity |
|---|---|---|---|
| 1 | Trailing commas create tuples in `__init__` | `pybloom.py:53-54` | Critical |
| 2 | `get_rows()` error path continues execution | `db_utils.py:30-37` | Critical |
| 3 | `temps_count` accumulates across observation sets | `pybloom.py:173,200` | Critical |
| 4 | `colours.html` uses fragile tuple indexing | `colours.html:14-15` | High |
| 5 | `base.html` references non-existent `brand.svg` | `base.html:32` | High |
| 6 | `base.html` missing `=` in aria-expanded | `base.html:37` | Medium |

### Should Fix (Architecture)

| # | Issue | Impact |
|---|---|---|
| 1 | Module-level side effects in `db_utils.py` | Testability, import safety |
| 2 | No error handling anywhere | Reliability |
| 3 | No logging | Observability |
| 4 | Monolithic `pybloom.py` | Maintainability |
| 5 | No dependency injection | Testability |
| 6 | Tight coupling in `app/__init__.py` | Testability, configurability |
| 7 | Hardcoded configuration | Flexibility, security |

### Should Improve (Code Quality)

| # | Issue | Impact |
|---|---|---|
| 1 | No type hints | Code clarity, IDE support |
| 2 | No docstrings | Documentation |
| 3 | No input validation | Robustness |
| 4 | Duplicate dependencies | Maintenance |
| 5 | SQL injection surface | Security |
| 6 | Bootstrap alpha version | Stability, security |

### Must Create (Testing)

| # | Issue | Impact |
|---|---|---|
| 1 | Actual test functions with assertions | Quality assurance |
| 2 | Test framework (pytest) | Test infrastructure |
| 3 | Test fixtures and mocks | Test isolation |
| 4 | CI/CD pipeline | Automated quality gates |
| 5 | Test coverage measurement | Visibility into test quality |

---

## 5. Recommended Implementation Order

1. **Fix critical bugs** (trailing commas, `get_rows` error path, `temps_count` accumulation)
2. **Add error handling and logging** throughout the codebase
3. **Restructure `pybloom.py`** into separate modules
4. **Refactor `db_utils.py`** to remove module-level side effects and add context managers
5. **Add dependency injection** to `WeatherObservation` and `HueLamp`
6. **Set up testing infrastructure** (pytest, conftest, fixtures, mocks)
7. **Write unit tests** for all core functions
8. **Add integration tests** for Flask routes
9. **Set up CI/CD** pipeline
10. **Add type hints and docstrings** across the codebase