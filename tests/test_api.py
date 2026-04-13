import pytest
from fastapi.testclient import TestClient
from web.backend.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_scoreboard_endpoint(client):
    resp = client.get("/api/scoreboard/2026-04-12")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) > 0
    game = data[0]
    assert "game_id" in game
    assert "home_team" in game
    assert "away_team" in game
    assert "status" in game


def test_scoreboard_no_games(client):
    resp = client.get("/api/scoreboard/2026-04-13")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)


def test_scoreboard_invalid_date(client):
    resp = client.get("/api/scoreboard/not-a-date")
    assert resp.status_code == 400


def test_boxscore_endpoint(client):
    resp = client.get("/api/game/0022501186/boxscore")
    assert resp.status_code == 200
    data = resp.json()
    assert "home" in data
    assert "away" in data
    assert "players" in data["home"]
    assert len(data["home"]["players"]) > 0


def test_playbyplay_endpoint(client):
    resp = client.get("/api/game/0022501186/playbyplay")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "description" in data[0]


def test_standings_endpoint(client):
    resp = client.get("/api/standings?season=2025-26")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 30


def test_player_stats_endpoint(client):
    resp = client.get("/api/stats/players?season=2025-26")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) > 100


def test_team_stats_endpoint(client):
    resp = client.get("/api/stats/teams?season=2025-26")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 30
