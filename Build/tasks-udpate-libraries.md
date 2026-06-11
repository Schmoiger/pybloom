# Library Upgrade Review

This document reviews every dependency in `requirements.txt`, compares the current pinned version against the latest release, and identifies breaking changes that affect the PyBloom codebase.

## Version comparison

| Library | Current | Latest | Breaking changes? |
|---------|---------|--------|-------------------|
| APScheduler | 3.6.3 | 3.11.2 | No |
| certifi | 2020.6.20 | 2026.5.20 | No |
| chardet | 3.0.4 | 7.4.3 | No (see note) |
| click | 7.1.2 | 8.4.1 | No (via Flask) |
| Flask | 1.1.2 | 3.1.3 | No |
| geojson | 2.5.0 | 3.3.0 | No (not used in app code) |
| idna | 2.10 | 3.18 | No |
| itsdangerous | 1.1.0 | 2.2.0 | No (via Flask) |
| Jinja2 | 2.11.2 | 3.1.6 | No |
| MarkupSafe | 1.1.1 | 3.0.3 | No (via Jinja2) |
| pygal | 2.4.0 | 3.1.0 | No |
| pyowm | 3.1.1 | 3.5.0 | No |
| PySocks | 1.7.1 | 1.7.1 | No change |
| pytz | 2020.1 | 2026.2 | No |
| qhue | 1.0.12 | 2.0.1 | No |
| requests | 2.24.0 | 2.34.2 | No |
| rgbxy | 0.5 | 0.5 | No change |
| six | 1.15.0 | 1.17.0 | Can remove |
| tzlocal | 2.1 | 5.3.1 | No |
| urllib3 | 1.25.11 | 2.7.0 | Must upgrade with requests |
| Werkzeug | 1.0.1 | 3.1.8 | No (via Flask) |
| python-dateutil | (unpinned) | 2.9.0.post0 | No |

---

## Per-library analysis

### 1. Flask 1.1.2 → 3.1.3

**Changes across major versions:**

- **Flask 2.0**: Dropped Python 2/3.5. Requires Click 8.0. Removed `flask.json.JSONEncoder`/`JSONDecoder`. Removed `before_first_request`.
- **Flask 2.2**: Deprecated `before_first_request` (removed in 2.3).
- **Flask 3.0**: Requires Python 3.8+. Removed `FLASK_ENV`/`ENV` config — use `FLASK_DEBUG`. Removed `TEMPLATE_AUTO_RELOAD`. `url_for()` no longer escapes `/` by default (no impact on our patterns).
- **Flask 3.1**: Requires Python 3.9+. Response class is now `werkzeug.wrappers.Response` directly.

**Impact on PyBloom: No code changes needed.**

- `from flask import Flask; app = Flask(__name__)` ✅ unchanged
- `@app.route('/')` and `@app.route('/index')` ✅ unchanged
- `render_template('index.html', title='Home', content=CONTENT)` ✅ unchanged
- `@app.after_request` with response header modification ✅ unchanged
- `url_for('static', filename='...')` and `url_for('index')` ✅ unchanged
- Jinja2 template syntax in all `.html` files ✅ unchanged

---

### 2. APScheduler 3.6.3 → 3.11.2

**Changes:** All within the 3.x series — backwards compatible. APScheduler 3.9+ prefers `zoneinfo` (stdlib) over `pytz` for timezone handling, but `pytz` still works as a fallback. Note: APScheduler 4.x has a completely new API, but we are not going there.

**Impact on PyBloom: No code changes needed.**

- `BackgroundScheduler(daemon=True)` ✅ unchanged
- `schedule.add_job(lambda: weather(), 'interval', minutes=10)` ✅ unchanged
- `schedule.start()` ✅ unchanged

---

### 3. Jinja2 2.11.2 → 3.1.6

**Changes:**

- Jinja2 3.0 requires Python 3.7+.
- Removed deprecated `contextfunction` and `contextfilter` (replaced by `pass_context` decorator). Only affects custom extensions, not regular templates.
- `Markup` class must be imported from `markupsafe`, not `jinja2`. PyBloom does not import `Markup` directly.
- Autoescaping is now enabled by default for `.html`, `.htm`, `.xml`, `.xhtml` templates. This is better security and does not cause issues with our templates.

**Impact on PyBloom: No code changes needed.**

- All template syntax (`{% extends %}`, `{% block %}`, `{% if %}`, `{{ url_for() }}`, `{{ title }}`) ✅ unchanged
- `render_template()` calls in `routes.py` ✅ unchanged

---

### 4. Werkzeug 1.0.1 → 3.1.8

**Changes:** Werkzeug is an internal dependency of Flask. Key changes:

- Werkzeug 2.0 requires Python 3.6+; Werkzeug 3.0 requires Python 3.8+.
- `werkzeug.utils.escape()` removed — use `markupsafe.escape()`. Not used in PyBloom.
- Request/Response classes reorganised — but Flask abstracts these.

**Impact on PyBloom: No code changes needed.** Flask handles all Werkzeug interactions internally.

---

### 5. Click 7.1.2 → 8.4.1

**Changes:** Click 8.0 requires Python 3.7+. Flask was updated to use Click 8.x for its CLI (`flask run`, `flask shell`, etc.).

**Impact on PyBloom: No code changes needed.** Flask CLI integration works transparently.

---

### 6. itsdangerous 1.1.0 → 2.2.0

**Changes:** itsdangerous 2.0 requires Python 3.7+. Flask uses itsdangerous internally for session signing. APIs (`Signer`, `TimedSerializer`, etc.) are largely unchanged.

**Impact on PyBloom: No code changes needed.** Note: PyBloom does not currently use Flask sessions or set `app.secret_key`, so this is entirely transparent.

---

### 7. MarkupSafe 1.1.1 → 3.0.3

**Changes:** MarkupSafe 2.0 requires Python 3.5+; 3.0 requires Python 3.7+. `soft_unicode()` removed in 2.1 (not used). `HTMLSanitizer` removed (not used).

**Impact on PyBloom: No code changes needed.** Jinja2 handles MarkupSafe integration internally.

---

### 8. pygal 2.4.0 → 3.1.0

**Changes:** pygal 3.x requires Python 3.7+. The chart API is backwards compatible — all constructor parameters, `add()`, `render_to_file()`, and `Style()` work identically.

**Impact on PyBloom: No code changes needed.**

- `pygal.Bar(x_label_rotation=20, ...)` ✅ unchanged
- `pygal.Pie(inner_radius=0.6, style=custom_style)` ✅ unchanged
- `pygal.Box(legend_at_bottom=True, ...)` ✅ unchanged
- `chart.add('name', data)` with dict-based values ✅ unchanged
- `chart.render_to_file(path)` ✅ unchanged
- `Style(colors=(...))` ✅ unchanged

---

### 9. pyowm 3.1.1 → 3.5.0

**Changes:** Minor version bump within 3.x — backwards compatible. Internal API improvements and bug fixes.

**Impact on PyBloom: No code changes needed.**

- `pyowm.OWM(OWM_KEY)` ✅ unchanged
- `owm.weather_manager()` ✅ unchanged
- `mgr.weather_at_place(location).weather` ✅ unchanged
- `weather.temperature('celsius')['temp']` ✅ unchanged
- `weather.detailed_status` ✅ unchanged

---

### 10. qhue 1.0.12 → 2.0.1

**Changes (from CHANGELOG and source code review):**

- **Requires Python 3 only** (dropped Python 2 support). PyBloom already requires Python 3.14, so no impact.
- **Added remote bridge access** (if not on LAN). New feature, not breaking.
- **`QhueException` now contains `type` and `address` info.** Additive change.
- **API patterns unchanged.** The `Resource` class uses `__call__` for GET/PUT/POST and `__getattr__`/`__getitem__` for attribute access. All existing patterns work identically.

**Impact on PyBloom: No code changes needed.**

- `qhue.Bridge(ip, username)` ✅ unchanged — same constructor signature
- `self.bridge.lights[lamp_id]()` ✅ unchanged — `__call__` does GET
- `self.bridge.lights[lamp_id].state(on=True)` ✅ unchanged — `.state` creates a Resource via `__getattr__`, calling it does PUT with kwargs
- `self.bridge.lights[lamp_id].state(xy=colour)` ✅ unchanged

---

### 11. requests 2.24.0 → 2.34.2

**Changes:** All within the 2.x series — backwards compatible. Key notes:

- requests 2.28+ switched default character detection from `chardet` to `charset-normalizer`.
- requests 2.32+ is required for full compatibility with `urllib3` 2.x.

**Impact on PyBloom: No code changes needed.** All `requests` calls go through qhue and pyowm libraries.

---

### 12. urllib3 1.25.11 → 2.7.0

**Changes:**

- urllib3 2.0 requires Python 3.7+.
- `urllib3.contrib.pyopenssl` removed (not used).
- SSL/TLS defaults changed to be stricter.
- **Must upgrade `requests` alongside `urllib3`** — requests 2.24.0 is NOT compatible with urllib3 2.x.

**Impact on PyBloom: No code changes needed**, but requests must be upgraded to 2.28+ (we are going to 2.34.2, which is fine).

---

### 13. chardet 3.0.4 → 7.4.3

**Changes:** chardet 5.0+ requires Python 3.7+. However, since requests 2.28+ uses `charset-normalizer` by default, `chardet` may no longer be needed as a direct dependency.

**Impact on PyBloom:** PyBloom does not use `chardet` directly — it is only a transitive dependency of requests. **Recommendation: Remove from `requirements.txt`** or replace with `charset-normalizer` if requests pulls it in.

---

### 14. geojson 2.5.0 → 3.3.0

**Note:** `geojson` is listed in `requirements.txt` but is not imported anywhere in the PyBloom codebase. It may be an unused dependency.

**Impact on PyBloom:** Can be removed from `requirements.txt` unless there are plans to use it.

---

### 15. pytz 2020.1 → 2026.2

**Changes:** Timezone data updates only. No API changes.

**Note:** APScheduler 3.9+ prefers `zoneinfo` (Python 3.9+ stdlib) over `pytz`. The `pytz` dependency could potentially be removed if APScheduler is configured to use `zoneinfo`, but keeping it is harmless.

---

### 16. python-dateutil (unpinned) → 2.9.0.post0

**Changes:** No breaking changes for the patterns used (`relativedelta`).

- `from dateutil.relativedelta import relativedelta` ✅ unchanged

**Note:** This dependency is already unpinned in `requirements.txt` — it will resolve to the latest version automatically.

---

### 17. Other dependencies (no changes needed)

| Library | Current → Latest | Notes |
|---------|-----------------|-------|
| certifi | 2020.6.20 → 2026.5.20 | CA certificate bundle updates only |
| idna | 2.10 → 3.18 | IDNA encoding updates only |
| PySocks | 1.7.1 → 1.7.1 | No change |
| rgbxy | 0.5 → 0.5 | No change |
| six | 1.15.0 → 1.17.0 | **Can be removed** — Python 2/3 compat layer no longer needed |
| tzlocal | 2.1 → 5.3.1 | Timezone detection still works; major version bump is due to API modernisation |

---

## Summary: Required code changes

### No code changes needed

The PyBloom codebase does not need any source code modifications to upgrade all libraries to their latest versions. All API patterns used across `pybloom.py`, `db_utils.py`, `app/__init__.py`, `app/routes.py`, `app/content.py`, and all templates are compatible with the latest versions.

### `requirements.txt` changes

1. **Update all version pins** to latest versions.
2. **Remove `chardet`** — replaced by `charset-normalizer` in requests 2.28+.
3. **Remove `six`** — Python 2/3 compatibility layer no longer needed.
4. **Consider removing `geojson`** — not imported anywhere in the codebase.
5. **Consider removing `pytz`** — APScheduler 3.9+ prefers stdlib `zoneinfo` (Python 3.9+).

### `pyproject.toml` changes

Update the `dependencies` list to match the new `requirements.txt` versions.

### Files that need NO changes

- `app.py` — no changes
- `app/__init__.py` — no changes
- `app/routes.py` — no changes
- `app/content.py` — no changes
- `db_utils.py` — no changes
- `pybloom.py` — no changes
- All `.html` templates — no changes