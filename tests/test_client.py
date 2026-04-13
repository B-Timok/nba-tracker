import json
from pathlib import Path
from nba_api.client import NBAClient

FIXTURES = Path(__file__).parent / "fixtures"


def test_parse_scoreboard():
    with open(FIXTURES / "scoreboard_20260412.json") as f:
        raw = json.load(f)

    client = NBAClient()
    games = client._parse_scoreboard(raw)

    assert len(games) > 0
    game = games[0]
    assert game.game_id == "0022501186"
    assert game.home_team.name == "Celtics"
    assert game.away_team.name == "Magic"
    assert game.home_team.score == 113
    assert game.away_team.score == 108
    assert game.is_final
    assert game.home_leader is not None
    assert game.home_leader.name == "Baylor Scheierman"


def test_parse_scoreboard_empty():
    raw = {"scoreboard": {"gameDate": "2026-04-13", "games": []}}
    client = NBAClient()
    games = client._parse_scoreboard(raw)
    assert games == []


def test_parse_boxscore():
    with open(FIXTURES / "boxscore_0022501186.json") as f:
        raw = json.load(f)

    client = NBAClient()
    home_box, away_box = client._parse_boxscore(raw)

    assert home_box.team.name == "Celtics"
    assert home_box.total_points == 113
    assert len(home_box.players) > 0

    starter_count = sum(1 for p in home_box.players if p.starter)
    assert starter_count == 5

    # Find Scheierman
    scheierman = next(p for p in home_box.players if "Scheierman" in p.name)
    assert scheierman.points == 30
    assert scheierman.starter is True

    assert away_box.team.name == "Magic"
    assert away_box.total_points == 108


def test_parse_playbyplay():
    with open(FIXTURES / "playbyplay_0022501186.json") as f:
        raw = json.load(f)

    client = NBAClient()
    actions = client._parse_playbyplay(raw)

    assert len(actions) > 0
    # First action should be period start
    assert actions[0].action_type == "period"
    assert actions[0].period == 1

    # Check that we have actions across multiple periods
    periods = {a.period for a in actions}
    assert len(periods) >= 4  # At least 4 quarters


def test_parse_standings():
    with open(FIXTURES / "standings_2025-26.json") as f:
        raw = json.load(f)

    client = NBAClient()
    entries = client._parse_standings(raw)

    assert len(entries) == 30  # 30 NBA teams

    # Thunder should be first (best record)
    thunder = next(e for e in entries if e.team_name == "Thunder")
    assert thunder.conference == "West"
    assert thunder.wins == 64
    assert thunder.losses == 18

    # Check both conferences exist
    conferences = {e.conference for e in entries}
    assert conferences == {"East", "West"}


def test_parse_player_stats():
    with open(FIXTURES / "player_stats_2025-26.json") as f:
        raw = json.load(f)

    client = NBAClient()
    stats = client._parse_player_stats(raw)

    assert len(stats) > 100  # Hundreds of players
    first = stats[0]
    assert first.player_name != ""
    assert first.gp > 0


def test_parse_team_stats():
    with open(FIXTURES / "team_stats_2025-26.json") as f:
        raw = json.load(f)

    client = NBAClient()
    stats = client._parse_team_stats(raw)

    assert len(stats) == 30
    first = stats[0]
    assert first.team_name != ""
    assert first.gp > 0
