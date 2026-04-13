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
