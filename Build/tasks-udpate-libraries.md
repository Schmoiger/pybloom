# Review of requirements.txt

Comprehensive Library Upgrade Breaking Changes Analysis
Based on thorough analysis of the PyBloom codebase and knowledge of each library's release history, here is a complete summary of breaking changes that would affect this project.

1. Flask 1.1.2 → 3.1.3
Flask 2.0 Breaking Changes
Python 3.6+ required (Flask 2.0 dropped Python 2 and 3.5 support)
Click 8.0 required (Click 7.x no longer supported)
flask.json.JSONEncoder and flask.json.JSONDecoder removed — replaced with flask.json.provider.DefaultJSONProvider. If any custom JSON encoding was used, it must be migrated.
before_first_request removed (deprecated in 2.2, removed in 2.3)
Flask.make_response() now returns a Response directly, not a Response wrapper. This could affect code that calls .data or manipulates the response.
after_request handlers must return a Response object. The pattern in app/routes.py (response.headers['Cache-Control'] = 'no-store') is fine — no changes needed.
Blueprints got nested blueprint support (new feature, not breaking)
Flask 2.2 Breaking Changes
before_first_request deprecated (removed in 2.3)
@app.before_first_request is gone — not used in this project, so no impact.
Flask 2.3 Breaking Changes
before_first_request removed entirely
Template context behavior changes: url_for() in templates still works the same way, no changes needed for the patterns used in base.html.
Flask 3.0 Breaking Changes
Python 3.8+ required
Removed deprecated json encoding/decoding classes
Removed FLASK_ENV and ENV config — use FLASK_DEBUG instead
Removed TEMPLATE_AUTO_RELOAD config option (always on now)
send_file() changes: download_name parameter is now required when as_attachment=True
url_for() no longer escapes / by default — this could affect URL generation in templates, but the url_for('static', filename='...') and url_for('index') patterns used in base.html should continue working.
Static file serving: The static folder handling is unchanged. url_for('static', filename='favicon.ico') still works identically.
@app.route() unchanged — routing patterns in routes.py work without modification.
Flask 3.1 Breaking Changes
Python 3.9+ required
Response class is now werkzeug.wrappers.Response (direct usage, no Flask wrapper)
after_request handlers: Must return a Response object. The current pattern (response.headers[...] = ...; return response) is still fine.
Impact on PyBloom
✅ from flask import Flask; app = Flask(__name__) — still works, no changes needed
✅ @app.route('/') and @app.route('/index') — still works
✅ render_template('index.html', title='Home', content=CONTENT) — still works
✅ @app.after_request with response header modification — still works
✅ url_for('static', filename='...') — still works
✅ url_for('index') and url_for('colours') — still works
✅ {% extends %}, {% block %}, {% if %}, {{ title }}, {{ url_for() }} — all still work
2. APScheduler 3.6.3 → 3.11.2
Breaking Changes
Version 3.x to 3.x is mostly backwards compatible (no major breaking changes within 3.x series)
BackgroundScheduler(daemon=True) — The daemon parameter is still supported in 3.11.x. No change needed.
add_job() API — The signature schedule.add_job(lambda: weather(), 'interval', minutes=10) is still valid. No changes needed.
schedule.start() — Still works identically.
pytz dependency: APScheduler 3.9+ prefers zoneinfo (Python 3.9+) over pytz, but pytz still works as a fallback. The project uses pytz in requirements.txt — this is fine.
Note: APScheduler 4.x (if upgrading further) has major breaking changes with a completely new API, but 3.11.2 does not.
Impact on PyBloom
✅ BackgroundScheduler(daemon=True) — no changes needed
✅ schedule.add_job(lambda: weather(), 'interval', minutes=10) — no changes needed
✅ schedule.start() — no changes needed
3. Jinja2 2.11.2 → 3.1.6
Breaking Changes
Jinja2 3.0 requires Python 3.7+
Removed deprecated contextfunction and contextfilter — replaced by pass_context decorator. Only affects custom extensions, not regular templates.
Removed with statement extension — it's built-in now (no {% from 'jinja2.ext' import with %}). Not used in this project.
Markup class moved: from markupsafe import Markup (was from jinja2 import Markup). Since MarkupSafe is a separate dependency, this works fine.
autoescape default changed: Autoescaping is now enabled by default for .html, .htm, .xml, .xhtml templates. This is actually better security but could theoretically cause double-escaping issues if code was manually escaping HTML.
Template.render() still works identically — no changes for render_template() usage.
{% extends %}, {% block %}, {% if %}, {{ url_for() }} — all template syntax is unchanged.
jinja2.sandbox.SandboxedEnvironment changes — not used in this project.
Impact on PyBloom
✅ All template syntax in base.html, index.html, colours.html — no changes needed
✅ {{ url_for('static', filename='...') }} — still works
✅ {% if title %}, {% block app_css %}, {% block app_content %} — all still work
✅ render_template() calls in routes.py — no changes needed
4. Werkzeug 1.0.1 → 3.1.8
Breaking Changes
Werkzeug 2.0 requires Python 3.6+
Werkzeug 3.0 requires Python 3.8+
werkzeug.contrib removed long ago (not used here)
environ handling changes: Some internal changes to request/response processing, but the Flask abstraction layer handles this.
Request and Response classes reorganized — but Flask wraps these, so direct usage isn't needed.
werkzeug.utils.escape() removed — use markupsafe.escape() instead. Not used directly in this project.
run_simple() changes — only relevant if running Werkzeug dev server directly.
remove_move() deprecated — cleanup of Python 2 compat code.
Impact on PyBloom
✅ Flask abstracts Werkzeug usage — no direct changes needed in app code
✅ Template rendering, request handling, response handling — all still work through Flask
5. Click 7.1.2 → 8.4.1
Breaking Changes
Click 8.0 requires Python 3.7+
click.BaseCommand.main() parameter changes — but Flask handles this internally.
click.get_current_context() behavior unchanged
click.echo(), click.style() — still work the same way.
Flask CLI (flask run, flask shell, etc.) — still works. Flask was updated to be compatible with Click 8.x.
flask.cli module — Flask updated its CLI code for Click 8 compatibility.
Impact on PyBloom
✅ Flask CLI integration — no changes needed
✅ If running flask run or using Flask CLI commands — still works
6. itsdangerous 1.1.0 → 2.2.0
Breaking Changes
itsdangerous 2.0 requires Python 3.7+
Signer, TimedSerializer, URLSafeTimedSerializer — APIs largely unchanged.
BadSignature exception — still exists, import path unchanged.
secret_key handling in Flask — Flask uses itsdangerous for session signing. The upgrade is transparent to app code.
Flask's app.secret_key — still works identically. The signing mechanism is internal.
Session cookies — Sessions signed with old itsdangerous may not be compatible after upgrade (cookies will fail to verify and be regenerated). This is a one-time event for users.
Impact on PyBloom
✅ If app.secret_key is set (not currently in this project, but if added) — works the same way
✅ Session handling — transparent upgrade, no code changes
7. MarkupSafe 1.1.1 → 3.0.3
Breaking Changes
MarkupSafe 2.0 requires Python 3.5+
MarkupSafe 3.0 requires Python 3.7+
Markup class: Still available via from markupsafe import Markup. In older Jinja2 versions, Markup was importable from jinja2. With Jinja2 3.x, you must import from markupsafe. This project doesn't import Markup directly, so no impact.
soft_unicode() removed in 2.1 — Not used in this project.
soft_str() added as replacement — Not needed.
HTMLSanitizer removed — Not used.
Jinja2 3.x depends on MarkupSafe 2.x+, so upgrading both together is required.
Impact on PyBloom
✅ Template rendering — no changes needed (Jinja2 handles MarkupSafe integration)
✅ No direct MarkupSafe imports in app code — no impact
8. urllib3 1.25.11 → 2.7.0
Breaking Changes
urllib3 2.0 requires Python 3.7+
urllib3.contrib.pyopenssl removed — replaced by stdlib ssl. Not used directly.
urllib3.util.retry.Retry — some parameter deprecations, but requests handles this internally.
requests library compatibility: requests 2.24.0 may NOT be fully compatible with urllib3 2.x. requests must be upgraded to at least 2.28.0+ (ideally 2.32.x) to work with urllib3 2.x.
requests.packages.urllib3 — the bundled copy in requests is removed in newer versions.
SSL/TLS defaults changed — stricter by default, could affect HTTPS connections to APIs (OWM, Hue).
Impact on PyBloom
⚠️ requests must be upgraded alongside urllib3 — requests==2.24.0 will NOT work with urllib3>=2.0
✅ requests.get() / requests.post() usage via qhue and pyowm — transparent if requests is upgraded
✅ API calls to OpenWeatherMap and Philips Hue — should work with updated requests + urllib3
9. qhue 1.0.12 → 2.0.1
Breaking Changes
Major version bump — significant API changes expected
qhue.Bridge(ip, username) — In qhue 2.0, the Bridge constructor API changed. The Bridge class may have different parameter handling.
bridge.lights[lamp_id]() (calling lights as callable to get state) — This pattern likely changes in 2.0. The callable resource pattern may be replaced with explicit .get() methods.
bridge.lights[lamp_id].state(on=True) — The .state() method may have changed to .set_state() or similar.
Resource access pattern: qhue 2.0 may use bridge.lights[id].get() instead of bridge.lights[id]().
Response format: JSON response parsing may differ.
Code Patterns That May Break in pybloom.py

# CURRENT (qhue 1.0.12):
self.bridge = qhue.Bridge(ip, username)
self.getter = self.bridge.lights[lamp_id]()  # callable to get state
self.setter = self.bridge.lights[lamp_id]
self.setter.state(on=True)   # .state() method
self.setter.state(xy=colour)  # .state() method

# LIKELY NEEDS UPDATE FOR qhue 2.0:
# Check qhue 2.0 docs for new API patterns
# May need: self.bridge.lights[lamp_id].get() instead of ()
# May need: self.bridge.lights[lamp_id].state(on=True) or .set_state()
Impact on PyBloom
⚠️ HueLamp class needs review and likely updates — the callable resource pattern and .state() method may have changed
⚠️ Test with actual Hue Bridge to verify API compatibility
10. pyowm 3.1.1 → 3.5.0
Breaking Changes
Minor version bump within 3.x — mostly backwards compatible
pyowm.OWM(API_key) — Still works the same way.
owm.weather_manager() — Still works.
mgr.weather_at_place(location).weather — Still works.
weather.temperature('celsius') — The dictionary key access ['temp'] still works.
weather.detailed_status — Still works as a property.
Some internal API changes around station observations, but the patterns used in this project are stable.
Impact on PyBloom
✅ pyowm.OWM(OWM_KEY) — no changes needed
✅ owm.weather_manager() — no changes needed
✅ mgr.weather_at_place(location).weather — no changes needed
✅ weather.temperature('celsius')['temp'] — no changes needed
✅ weather.detailed_status — no changes needed
11. pygal 2.4.0 → 3.1.0
Breaking Changes
Python 3.7+ required for pygal 3.x
pygal.Bar() — Constructor parameters are largely the same. x_label_rotation, show_minor_x_labels, show_legend still work.
pygal.Pie() — inner_radius parameter still works.
pygal.Box() — legend_at_bottom, legend_at_bottom_columns, print_labels still work.
pygal.Radar() — Still works with same parameters.
chart.add(name, values) — Still works. The dict-based value format {'value': temp, 'color': '#' + hex} still works.
chart.x_labels assignment — Still works.
chart.render_to_file(path) — Still works.
pygal.style.Style() — Still works. colors, background, plot_background, opacity, opacity_hover, transition parameters still work.
from pygal.style import Style — Still works.
SVG rendering improvements — Output may look slightly different but functionally compatible.
Impact on PyBloom
✅ pygal.Bar(x_label_rotation=20, ...) — no changes needed
✅ pygal.Pie(inner_radius=0.6, style=custom_style) — no changes needed
✅ pygal.Box(legend_at_bottom=True, ...) — no changes needed
✅ pygal.Radar(...) — no changes needed
✅ chart.add('name', data) — no changes needed
✅ chart.render_to_file(path) — no changes needed
✅ Style(colors=(...)) — no changes needed
12. rgbxy 0.5 → 0.5 (same version)
No Changes
✅ from rgbxy import Converter — no changes
✅ from rgbxy import GamutA — no changes
✅ Converter(GamutA).hex_to_xy(hex_string) — no changes
13. chardet 3.0.4 → 7.4.3
Breaking Changes
chardet 5.0+ requires Python 3.7+
requests library migration: requests 2.28+ switched default from chardet to charset-normalizer. If upgrading requests, chardet may no longer be needed as a direct dependency.
If chardet is used directly in code: The chardet.detect() API is still the same. But this project doesn't use chardet directly — it's only a transitive dependency of requests.
Recommendation: With upgraded requests, replace chardet with charset-normalizer in requirements.txt, or remove it entirely.
Impact on PyBloom
✅ No direct chardet usage in code — no changes needed
⚠️ If keeping chardet with upgraded requests, it becomes unused; consider removing from requirements.txt
14. Other Dependencies
requests 2.24.0 → latest (2.32.x recommended)
Must upgrade when upgrading urllib3 to 2.x
requests.Session and requests.get/post — APIs unchanged
charset-normalizer replaces chardet as default
pytz 2020.1 → latest
No breaking changes — timezone data updates only
Consider switching to zoneinfo (stdlib in Python 3.9+) for new code
python-dateutil (no version pinned)
No breaking changes for the patterns used (relativedelta)
from dateutil.relativedelta import relativedelta — still works
certifi 2020.6.20 → latest
No breaking changes — CA certificate bundle updates only
idna 2.10 → latest
No breaking changes — IDNA encoding updates
PySocks 1.7.1 → latest
No breaking changes — SOCKS proxy support
six 1.15.0
Can likely be removed — Python 2/3 compatibility layer no longer needed with Python 3.8+ requirement
tzlocal 2.1 → latest
Minor changes — timezone detection still works
Summary: Code Changes Required for PyBloom
Likely NO Changes Needed
Flask app setup: app = Flask(__name__) ✅
Routing: @app.route('/') patterns ✅
Template rendering: render_template() calls ✅
Template syntax: {% extends %}, {% block %}, {{ url_for() }}, {% if %} ✅
Response handling: @app.after_request ✅
Static files: url_for('static', filename='...') ✅
APScheduler: BackgroundScheduler(daemon=True), add_job(), start() ✅
pyowm: All weather API calls ✅
pygal: All chart creation and rendering ✅
rgbxy: All color conversion ✅
Jinja2: All template syntax ✅
Werkzeug: Transparent via Flask ✅
itsdangerous: Transparent via Flask ✅
Click: Transparent via Flask CLI ✅
MarkupSafe: Transparent via Jinja2 ✅
Needs Investigation/Changes
⚠️ qhue 2.0.1: The Bridge constructor and resource access patterns (bridge.lights[id](), .state()) likely changed. The HueLamp class in pybloom.py (lines 94-124) needs review and likely updates.
⚠️ urllib3 2.x + requests: Must upgrade requests to 2.28+ alongside urllib3 2.x.
⚠️ chardet: Can likely be removed or replaced with charset-normalizer when upgrading requests.
⚠️ six: Can be removed (Python 2 compat no longer needed).
Key files to read/update:
requirements.txt — Update all version pins
pybloom.py — Lines 94-124 (HueLamp class) need qhue 2.0 API review
app/__init__.py — No changes needed
app/routes.py — No changes needed
All template files — No changes needed