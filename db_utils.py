'''
Create sqlite3 database containing two tables. Pre-populate Hue colours db.
'''

import sqlite3
DEFAULT_DB = 'database.sqlite3'


def db_connect(db_file=DEFAULT_DB):
    # create connection to SQLite database
    connection = sqlite3.connect(db_file)
    return connection


# utility function, handles opening and closing the database connection
def get_rows(table, columns='*', **kwargs):
    # columns_names should be a string enclosing a tuple of selected columns
    if (table == 'colours') or (table == 'observations'):
        con = db_connect()  # connect to the database
        cur = con.cursor()  # instantiate a cursor obj
        con.row_factory = sqlite3.Row

        rows_sql = ''
        args = ()
        for key, value in kwargs.items():
            if key == 'rows_sql':
                rows_sql = ' ' + value
            elif key == 'args':
                args = value
        if rows_sql.count('?') != len(args):
            results = 'Unexpected number of arguments in row modifier'

        cur.execute('SELECT ' + columns + ' FROM ' + table + rows_sql, args)
        results = cur.fetchall()
    else:
        results = 'invalid table name'
    con.close()  # close connection
    return results


con = db_connect()  # connect to the database
cur = con.cursor()  # instantiate a cursor obj

# create table of Hue Bloom colours if one doesn't already exist
colours_sql = """
CREATE TABLE IF NOT EXISTS colours (
    id integer PRIMARY KEY,
    temperature integer UNIQUE,
    hex_value text NOT NULL)"""
cur.execute(colours_sql)

# create table of weather observations if one doesn't already exist
observations_sql = """
CREATE TABLE IF NOT EXISTS observations (
    id integer PRIMARY KEY,
    timestamp text UNIQUE,
    temperature real NOT NULL,
    detailed_status text NOT NULL)"""
cur.execute(observations_sql)

# populate Hue colours db with default values if doesn't already exist
temp_colours = {  # from https://www.w3schools.com/colors/colors_picker.asp
    40: 'ff0000',  # colour value if temperature is >= than key
    35: 'ff4000',  # note: value is string, not hex
    30: 'ff8000',
    25: 'ffbf00',
    20: 'ffff00',
    15: 'bfff00',
    10: '00ff80',
    5: '00ffbf',
    0: '00ffff',
    -5: '00bfff',
    -10: '0080ff',
    -15: '0040ff'
}

colours_sql = '''INSERT OR IGNORE INTO colours (temperature, hex_value)
                 VALUES (?, ?)'''
for temperature, hex_value in temp_colours.items():
    cur.execute(colours_sql, (temperature, hex_value))

con.commit()
con.close()  # close connection

'''
# DEBUG:
sql = 'WHERE temperature = (?)'
what = (temperature, )  # tuple with single item
results = get_rows('colours', 'hex_value', rows_sql=sql, args=what)
print(results[0][0])
'''
