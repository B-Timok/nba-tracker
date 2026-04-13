"""Live integration tests — hit the real NBA API.

Run with: pytest tests/test_integration.py -v -m integration
Skip in CI or offline: these are excluded by default.
"""
import pytest
from datetime import date
from nba_api import NBAClient, game_date_to_season

pytestmark = pytest.mark.integration


@pytest.fixture
def client():
    return NBAClient()


def test_live_scoreboard(client):
    """Fetch today's scoreboard from the real API."""
    games = client.get_scoreboard(date.today())
    assert isinstance(games, list)


def test_live_historical_scoreboard(client):
    """Fetch a known historical date with games."""
    games = client.get_scoreboard(date(2026, 4, 12))
    assert len(games) > 0
    game = games[0]
    assert game.game_id != ""
    assert game.home_team.name != ""


def test_live_boxscore(client):
    """Fetch box score for a known completed game."""
    home, away = client.get_boxscore("0022501186")
    assert home.total_points > 0
    assert away.total_points > 0
    assert len(home.players) > 0


def test_live_playbyplay(client):
    """Fetch play-by-play for a known completed game."""
    actions = client.get_playbyplay("0022501186")
    assert len(actions) > 100


def test_live_standings(client):
    """Fetch current season standings."""
    season = game_date_to_season(date.today())
    entries = client.get_standings(season)
    assert len(entries) == 30


def test_live_player_stats(client):
    season = game_date_to_season(date.today())
    stats = client.get_player_stats(season)
    assert len(stats) > 100


def test_live_team_stats(client):
    season = game_date_to_season(date.today())
    stats = client.get_team_stats(season)
    assert len(stats) == 30
