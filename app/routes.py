"""Flask routes for the PyBloom web app."""

from flask import render_template
from app import app
from app import content


CONTENT = content.graphs()


@app.route('/')
@app.route('/index')
def index() -> str:
    """Render the main dashboard."""
    return render_template('index.html', title='Home', content=CONTENT)


@app.route('/colours')
def colours() -> str:
    """Render the temperature-to-colour reference table."""
    return render_template('colours.html', title='Colours', rows=content.colours_table())


@app.after_request
def after_request_func(response):
    """Disable browser caching so the dashboard reflects fresh data."""
    response.headers['Cache-Control'] = 'no-store'
    return response
