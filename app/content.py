"""Small content helpers for templates."""

from typing import Any

from db_utils import get_rows


def graphs() -> dict[str, str]:
    """Return the static graph filenames used by the dashboard."""
    return {
        'lastday': 'last_day_radar.svg',
        'lastweek': 'last_week_bar.svg',
        'lastmonth': 'last_month_pie.svg',
        'lastyear': 'last_year_box.svg'
    }


def colours_table() -> list[Any]:
    """Return the colour mapping rows for the colours page."""
    return get_rows('colours')
