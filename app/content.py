'''
Rudimentary content management script
'''

from db_utils import get_rows


def graphs():
    all_graphs = {
        'lastday': 'last_day_bar.svg',
        'lastweek': 'last_week_bar.svg',
        'lastmonth': 'last_month_pie.svg'
    }
    return all_graphs


def colours_table():
    rows = get_rows('colours')
    return rows
