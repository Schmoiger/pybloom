'''
Rudimentary content management script
'''

from db_utils import get_rows


def graphs():
    all_graphs = {
        'lastday': 'last_day_bar.svg',
        'lastweek': 'last_week_pie.svg',
        'lastmonth': 'last_month_bar.svg'
    }
    return all_graphs


def colours_table():
    rows = get_rows('colours')
    return rows
