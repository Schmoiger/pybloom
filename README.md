# PyBloom

Indicate the outside temperature on Philips Hue lights.

PyBloom fetches the current weather from the Open Weather Map API, maps the temperature to a colour, and sets the colour on your Philips Hue Bloom lights. It also logs observations to a local SQLite database and generates temperature graphs served via a Flask web app.

## Prerequisites

- Python 3.14+
- [uv](https://docs.astral.sh/uv/) package manager
- A [Philips Hue](https://developers.meethue.com/) Bridge and Bloom light(s)
- A free [Open Weather Map](https://openweathermap.org/api) API key

## Setup

### 1. Install dependencies

```bash
uv sync
```

### 2. Create a credentials file

Create a file called `credentials.py` in the project root (this file is gitignored):

```python
credentials = {
    'hue_ip': '<IP address of your Hue Bridge>',
    'hue_username': '<given by the Hue Bridge on first sync>',
    'owm_key': '<your Open Weather Map API key>',
    'home_location': '<where you live, e.g. "London, GB">'
}
```

To obtain your Hue Bridge IP and username, follow the [Philips Hue getting started guide](https://developers.meethue.com/develop/get-started-2/).

### 3. Initialise the database

The SQLite database (`database.sqlite3`) is created automatically on first run. No manual setup is required.

## Running

### Development (local machine)

```bash
uv run flask run
```

The app will be available at `http://127.0.0.1:5000`.

The background scheduler starts automatically and fetches weather observations every 10 minutes, updating the Hue lights and generating graphs.

### Raspberry Pi / network access

To make the web app accessible to other devices on your local network:

```bash
uv run flask run --host=0.0.0.0
```

Then open `http://<IP address of your Pi>:5000/` in a browser.

### Running pybloom.py directly

You can also run the weather observation script standalone (without the web server):

```bash
uv run python pybloom.py
```

This will fetch a single observation, update the Hue lights, log to the database, and generate graphs.

## Web pages

| Route | Description |
|-------|-------------|
| `/` or `/index` | Dashboard with temperature graphs (last 24 hours, last week) |
| `/colours` | Colour key table showing the temperature-to-colour mapping |

## Project structure

```
pybloom/
├── app.py                  # Flask entry point
├── pybloom.py              # Weather observation, Hue lamp, and graph generation
├── db_utils.py             # SQLite database setup and query utilities
├── credentials.py          # API keys (gitignored)
├── app/
│   ├── __init__.py         # Flask app initialisation and APScheduler setup
│   ├── routes.py           # Flask routes
│   ├── content.py          # Content management (graph paths, colour table)
│   ├── templates/          # Jinja2 HTML templates
│   │   ├── base.html
│   │   ├── index.html
│   │   └── colours.html
│   └── static/             # Static assets (favicons, logos)
├── tests/
│   └── test.py
├── docs/
│   └── PyBloom_manual.md   # Detailed development manual
├── pyproject.toml
├── requirements.txt
└── .python-version
```

## Technologies

- **Flask** – web framework
- **SQLite** – local database for observations and colour mappings
- **PyOWM** – Python wrapper for the Open Weather Map API
- **Qhue / rgbxy** – Philips Hue API wrapper and colour space conversion
- **PyGal** – lightweight graphing library for SVG charts
- **APScheduler** – background job scheduling (weather fetch every 10 minutes)
- **Bootstrap CSS** – responsive web design
- **Jinja2** – HTML templating for Flask

## Further reading

See [docs/PyBloom_manual.md](docs/PyBloom_manual.md) for a detailed development manual covering the architecture, design decisions, and step-by-step code walkthrough.