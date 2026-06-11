# Testing Implementation Plan

Pragmatic plan for adding tests to PyBloom. The goal is to cover the parts that would actually break the app if they regressed, not to build a heavyweight enterprise test harness.

---

## 1. Bugs

### 1.1 `tests/test.py` is not a real test suite

**File:** `tests/test.py`

The current file is a script that generates an SVG and contains commented-out exploratory code. It does not define test functions, so test runners will not treat it as a suite.

Why this matters:
- there is no repeatable automated verification
- the file name suggests tests that do not exist

**Recommendation:** Replace it with real `pytest` tests under `tests/test_*.py`.

---

### 1.2 The code is not yet test-friendly

**Files:** `db_utils.py`, `pybloom.py`, `app/__init__.py`

Import-time database work, scheduler startup during app import, and live constructor calls make the current code awkward to test.

Why this matters:
- tests can accidentally touch the real database
- imports can trigger network calls or scheduler side effects

**Recommendation:** Make the small refactors already identified in [tasks-improve-code.md](/Users/avi/Repos/pybloom/Build/tasks-improve-code.md) first, then add tests. That is enough for this project; do not over-engineer the design just for testability.

---

### 1.3 `colours.html` indexes rows by position

**File:** `app/templates/colours.html`

The template uses `row[1]` and `row[2]` rather than named access. That is brittle if the query shape changes.

**Recommendation:** Use `row['temperature']` and `row['hex_value']`. This is a small fix, but it also makes template tests clearer.

---

## 2. Cleanup

### 2.1 Add `pytest` and coverage support

**File:** `pyproject.toml`

The repo currently has no testing toolchain configured.

**Recommendation:**
- add `pytest`
- add `pytest-cov` if you want coverage reporting
- add a small pytest config section

Do not lock yourself into a 95% coverage target at the start. That is the wrong metric for this codebase while the suite is still being built.

---

### 2.2 Add a small fixture set

**Files:** `tests/conftest.py`

You only need a few reusable fixtures:

- in-memory SQLite database
- sample observations for graph tests
- Flask test client
- temporary SVG output directory
- simple mocks for OWM and Hue

**Recommendation:** Keep fixtures minimal and shared. Avoid a large fixture matrix unless the tests actually need it.

---

### 2.3 Split exploratory code out of `tests/test.py`

**File:** `tests/test.py`

The existing file mixes ad hoc experimentation with a sketch of graph generation.

**Recommendation:** Delete the script-style file and replace it with focused test modules. If you need a manual experiment script, keep it separate from the test suite.

---

## 3. Nice-to-have

### 3.1 Test the database helpers first

**Target:** `db_utils.py`

This is the lowest-risk place to start because it is deterministic and has few dependencies.

Good initial tests:
- `db_connect()` returns a connection
- `get_rows()` returns rows for both tables
- invalid table handling is explicit
- `init_db()` creates and seeds the schema

---

### 3.2 Test the pure logic in `pybloom.py`

**Target:** `pybloom.py`

The most valuable tests are the ones that check logic that should not change silently:

- `find_temp_threshold()`
- `lookup_colour()`
- `convert_temp_to_colour()`
- `WeatherObservation.__str__()`
- `WeatherObservation.set()`

These are worth testing before the more integration-heavy pieces.

---

### 3.3 Test the orchestration path with mocks

**Target:** `weather()`

You do not need to hit live services in tests. Mock the OWM and Hue layers and verify the orchestration:

- observation is fetched
- lamp colour is set
- observation is logged
- graphs are generated

This is enough to protect the top-level workflow without brittle integration tests.

---

### 3.4 Test the Flask routes lightly

**Targets:** `app/routes.py`, templates

Add a couple of route tests that confirm:

- the home page renders
- the colours page renders
- expected context data reaches the templates

**Recommendation:** Keep route tests shallow. You do not need to test Bootstrap or every HTML detail.

---

### 3.5 Coverage reporting

**Optional target:** `pyproject.toml`

Coverage is useful as a guide, but it should not become the goal.

**Recommendation:** Track coverage locally, but treat it as a sanity check rather than a hard project requirement until the suite is mature.

---

## 4. What I Would Not Prioritise Yet

These were in the original plan, but they are too much for this project at this stage:

- building a 95% coverage target up front
- `responses` plus a large external-mock stack
- a very large `conftest.py`
- broad integration tests against live services
- testing every SVG output path in detail
- adding fixtures for every possible dependency combination

Those ideas are valid in larger projects, but they would add more setup cost than value here. Start with a small, reliable suite and expand it only where you actually feel pain.

