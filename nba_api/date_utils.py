from datetime import date, timedelta
from typing import Optional


def parse_game_date(date_str: str) -> Optional[date]:
    """Parse a YYYY-MM-DD string into a date. Returns None if invalid."""
    try:
        return date.fromisoformat(date_str)
    except (ValueError, TypeError):
        return None


def next_day(d: date) -> date:
    return d + timedelta(days=1)


def prev_day(d: date) -> date:
    return d - timedelta(days=1)


def game_date_to_season(d: date) -> str:
    """Convert a game date to NBA season string (e.g., '2025-26').

    NBA seasons start in October and end in June.
    Dates from October onward use that year as the start.
    Dates before October use the previous year as the start.
    """
    if d.month >= 9:
        start_year = d.year
    else:
        start_year = d.year - 1
    end_year = start_year + 1
    return f"{start_year}-{str(end_year)[-2:]}"
