from flask import render_template
from app import app
from app import content


CONTENT = content.graphs()
COLOURS_TABLE = content.colours_table()


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Home', content=CONTENT)
@app.route('/colours')
def colours():
    return render_template('colours.html', title='Colours', rows=COLOURS_TABLE)
@app.after_request
def after_request_func(response):
    response.headers['Cache-Control'] = 'no-store'
    return response
