# Codebase Improvement Review

Pragmatic review of the PyBloom codebase, focused on fixes that are worth doing for a home project. The aim here is not commercial-grade architecture; it is to remove real bugs, reduce fragility, and make the code easier to change without over-engineering it.

---

## 1. Bugs

### 1.1 Module-level side effects in `db_utils.py`
✅ DONE

**File:** `db_utils.py`

Database schema creation and seed insertion happen at import time. That means importing `db_utils` from anywhere will open a database connection and potentially create or modify files on disk.

Why this matters:
- Tests can accidentally touch the real database
- Import-time failures are harder to diagnose
- The module does more work than a utility module should do

**Recommendation:** Move schema creation and seed insertion into an explicit `init_db()` function, and call it from the app startup path only.

---

### 1.2 `WeatherObservation.__init__` has a real bug
✅ DONE

**File:** `pybloom.py`

The trailing commas on `timestamp` and `temperature` create single-item tuples instead of assigning the values directly.

**Recommendation:** Remove the commas.

---

### 1.3 `get_rows()` has broken error handling
✅ DONE

**File:** `db_utils.py`

If the argument count does not match, the function assigns an error string but still continues into `cur.execute()`. There is also a control-flow issue when the table name is invalid because `con.close()` is still reached even when no connection was created.

Why this matters:
- Errors are hidden instead of stopping the bad query
- The function can fail in confusing ways

**Recommendation:** Return or raise immediately on invalid input, and use a `try` / `finally` or context manager so connections are always closed safely.

---

### 1.4 Scheduler startup happens at import time
✅ DONE

**File:** `app/__init__.py`

The Flask app imports routes and then starts the background scheduler immediately.

Why this matters:
- Tests import the app and get side effects
- The scheduler cannot be started or stopped cleanly
- It is harder to control startup order

**Recommendation:** Move scheduler startup into a small factory function or app startup hook. Keep the interval configurable, but avoid turning this into a full framework.

---

### 1.5 `WeatherObservation.new()` is misleadingly named
✅ DONE

**File:** `pybloom.py`

The method mutates the existing object and returns a status string. It does not create a new object.

**Recommendation:** Rename it to `fetch()` or `update()`. This is a small cleanup, but it improves readability.

---

## 2. Cleanup

### 2.1 Use context management for database access
✅ DONE

**Files:** `db_utils.py`, `pybloom.py`

Database connections are opened and closed manually in multiple places. That is workable, but it is easy to forget cleanup if an exception occurs.

**Recommendation:** Wrap connection handling in a context manager so `close()` is always guaranteed. This is enough for a small SQLite app; you do not need connection pooling.

---

### 2.2 Add basic error handling around external calls
✅ DONE

**Files:** `pybloom.py`

Weather fetches, Hue calls, and database writes can all fail. Right now, failures will bubble up and may stop the scheduler job.

Why this matters:
- Network hiccups are normal
- One failed run should not break the next run

**Recommendation:** Add small `try` / `except` blocks around external calls and log the failure. Retry logic and circuit breakers are probably more than this project needs.

---

### 2.3 Replace `print()` with logging
✅ DONE

**File:** `pybloom.py`

The code prints to stdout instead of using the logging module. On the Pi, logging to the console still gives visible feedback, so this is about routing status messages through `logging`, not hiding them.

**Recommendation:** Use Python `logging` with a simple console configuration. No need for a complex logging stack; just make failures and job progress visible.

---

### 2.4 `temps_count` should be reset per graph period
✅ DONE

**File:** `pybloom.py`

The pie chart counts are accumulated across iterations of the loop, so later graphs include earlier counts.

**Recommendation:** Recreate `temps_count` inside each loop iteration.

---

### 2.5 `lookup_colour()` assumes data always exists
✅ DONE

**File:** `pybloom.py`

If the database returns no matching row, `results[0]` raises `IndexError`.

**Recommendation:** Check for an empty result set and fail with a clear error message.

---

### 2.6 `HueLamp.set_colour()` makes two API calls
✅ DONE

**File:** `pybloom.py`

The light is turned on and then recoloured in separate calls.

**Recommendation:** Use one state update call if the API supports it. This is a tidy efficiency improvement, not a blocker.

---

### 2.7 `COLOURS_TABLE` is loaded once at import time
WON'T FIX - Colours are static

**File:** `app/routes.py`

The colours table is read once when the module is imported. If the database changes, the route will not see new data until the app is restarted.

**Recommendation:** Fetch the table inside the route handler if you want live updates. If the data is effectively static, this can stay as-is.

---

### 2.8 Bootstrap navbar markup is mismatched with the included version
✅ DONE

**File:** `app/templates/base.html`

The navbar uses Bootstrap 4-style attributes such as `data-toggle` and `data-target`, but the page includes a Bootstrap 5 alpha bundle. The toggle button is also missing the `#` prefix in the target selector, and the `aria-expanded` attribute is malformed.

Why this matters:
- the mobile navbar toggle may not work
- the page is mixing Bootstrap versions and patterns

**Recommendation:** Update the navbar markup to match the Bootstrap version actually being used. This is a small but real functional fix.

---

### 2.9 Template alt text is duplicated and inaccurate
✅ DONE

**File:** `app/templates/index.html`

The image alt text for the last two graphs says “last week” even when the graph is for the month or year.

Why this matters:
- it is misleading for screen readers
- it makes the page slightly less trustworthy

**Recommendation:** Fix the alt text so each graph describes the correct time range.

---

## 3. Nice-to-have

### 3.1 Repeated database lookups in `find_temp_threshold()`

**File:** `pybloom.py`

The temperature thresholds are read from the database each time the helper is called.

**Recommendation:** Cache the threshold list if you want to reduce repeated queries. This is a reasonable cleanup, but not urgent for a small dataset.

---

### 3.2 Imports inside `generate_graphs()`
✅ DONE

**File:** `pybloom.py`

`statistics.mean` and `dateutil.relativedelta` are imported inside the function body.

**Recommendation:** Move them to the top of the file unless there is a specific circular-import reason. This is style-level cleanup.

---

### 3.3 Duplicate dependency files

**Files:** `requirements.txt`, `pyproject.toml`

Both files define dependencies. That can drift over time.

**Recommendation:** If `uv` is the main workflow, prefer `pyproject.toml` as the source of truth and keep `requirements.txt` only if you actually need it for deployment compatibility.

---

### 3.4 Type hints and docstrings

**Files:** All Python files

The code has very few type hints and only sparse docstrings.

**Recommendation:** Add type hints and short docstrings where they help readability. Do not force a full typing pass if it slows you down more than it helps.

✅ DONE: Added module docstrings and focused type hints to the public helpers, Flask routes, and the weather/Hue classes.

---

### 3.5 Formal migrations and health endpoints

**Files:** `db_utils.py`, app code

There is no migration framework or `/health` endpoint.

**Recommendation:** Only add these if you actually feel pain from schema changes or deployment monitoring. For a home Raspberry Pi project, these are optional, not baseline requirements.

---

## 4. What I Would Not Prioritise Yet

These were in the original review, but they are probably too much for this project unless you specifically want the extra structure:

- Dependency injection everywhere
- A migration tool such as Alembic
- Circuit breakers for the Hue bridge
- Metrics collection and observability dashboards
- Connection pooling for SQLite
- A split into five separate modules immediately

Those ideas are valid in larger systems, but they add complexity faster than they add value here. If you refactor, do it incrementally and only where the current code is clearly hurting you.
