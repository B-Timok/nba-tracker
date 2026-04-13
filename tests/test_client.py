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
