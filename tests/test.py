
# need to import modules from files in parent directory
# https://codeolives.com/2020/01/10/python-reference-module-in-parent-directory/
import os
import sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)
from pybloom import lookup_colour, find_temp_threshold
import pygal
import db_utils


# testing graphing methods
FILEPATH = './tests/test'
rows = db_utils.get_rows('observations')
times = [row['timestamp'] for row in rows]
temps = [row['temperature'] for row in rows]

bar_chart = pygal.Bar(x_label_rotation=20,
                      x_labels_major_count=6,
                      show_minor_x_labels=False,
                      show_legend=False)
bar_chart.add('Temperature', [
    {'value': temp,
     'color': '#'+lookup_colour(find_temp_threshold(temp))}
    for temp in temps]
)
bar_chart.x_labels = times
filename = FILEPATH + '_bar.svg'
bar_chart.render_to_file(filename)

'''
# testing methods to access database
# results = db_utils.get_rows('colours')

con = db_utils.sqlite3.connect(db_utils.DEFAULT_DB)
con.row_factory = db_utils.sqlite3.Row
cur = con.cursor()
columns = '*'
table = 'colours'
cur.execute('SELECT ' + columns + ' FROM ' + table)
results = cur.fetchall()
con.close()

print(type(results))
print(type(results[0]))
print(results[1]['hex_value'])
'''
