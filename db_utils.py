"""SQLite database helpers for schema setup and row retrieval."""

import sqlite3
from collections.abc import Sequence
from typing import Any

DEFAULT_DB = 'database.sqlite3'


def db_connect(db_file: str = DEFAULT_DB) -> sqlite3.Connection:
    """Create a SQLite connection for the configured database file."""
    connection = sqlite3.connect(db_file)
    return connection


def init_db(db_file: str = DEFAULT_DB) -> None:
    """Create tables and seed default colour thresholds."""
    con = db_connect(db_file)
    cur = con.cursor()

    try:
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
    finally:
        con.close()


def get_rows(
    table: str,
    columns: str = '*',
    **kwargs: Any,
) -> list[sqlite3.Row]:
    """Return rows from a known table.

    Optional kwargs:
    - rows_sql: additional SQL fragment beginning with WHERE/ORDER BY
    - args: sequence of query parameters for the fragment
    """
    if (table == 'colours') or (table == 'observations'):
        con = db_connect()
        con.row_factory = sqlite3.Row
        cur = con.cursor()

        try:
            rows_sql = ''
            args: Sequence[Any] = ()
            for key, value in kwargs.items():
                if key == 'rows_sql':
                    rows_sql = ' ' + value
                elif key == 'args':
                    args = value
            if rows_sql.count('?') != len(args):
                raise ValueError('Unexpected number of arguments in row modifier')

            cur.execute('SELECT ' + columns + ' FROM ' + table + rows_sql, args)
            return cur.fetchall()
        finally:
            con.close()
    else:
        raise ValueError('invalid table name')
