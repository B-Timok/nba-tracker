from datetime import date
from nba_api.date_utils import parse_game_date, next_day, prev_day, game_date_to_season


def test_parse_today():
    result = parse_game_date("2026-04-13")
    assert result == date(2026, 4, 13)


def test_parse_iso_format():
    result = parse_game_date("2026-04-12")
    assert result == date(2026, 4, 12)


def test_parse_invalid_date():
    result = parse_game_date("not-a-date")
    assert result is None


def test_next_day():
    d = date(2026, 4, 12)
    assert next_day(d) == date(2026, 4, 13)


def test_prev_day():
    d = date(2026, 4, 13)
    assert prev_day(d) == date(2026, 4, 12)


def test_game_date_to_season_fall():
    """October 2025 is in the 2025-26 season."""
    assert game_date_to_season(date(2025, 10, 15)) == "2025-26"


def test_game_date_to_season_spring():
    """April 2026 is still in the 2025-26 season."""
    assert game_date_to_season(date(2026, 4, 13)) == "2025-26"


def test_game_date_to_season_summer():
    """July 2026 is in the 2025-26 season (offseason maps to previous)."""
    assert game_date_to_season(date(2026, 7, 15)) == "2025-26"


def test_game_date_to_season_september():
    """September 2025 maps to upcoming 2025-26 season."""
    assert game_date_to_season(date(2025, 9, 15)) == "2025-26"
