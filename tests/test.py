
# need to import modules from files in parent directory
# https://codeolives.com/2020/01/10/python-reference-module-in-parent-directory/
import os
import sys
currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

import db_utils


# testing methods to access database

results = db_utils.get_rows('colours')
'''
con = db_utils.sqlite3.connect(db_utils.DEFAULT_DB)
con.row_factory = db_utils.sqlite3.Row
cur = con.cursor()
columns = '*'
table = 'colours'
cur.execute('SELECT ' + columns + ' FROM ' + table)
results = cur.fetchall()
con.close()
'''
print(type(results))
print(type(results[0]))
print(results[1]['hex_value'])
