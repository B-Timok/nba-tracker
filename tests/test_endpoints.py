from nba_api.endpoints import NBAEndpoints


def test_scoreboard_today():
    url = NBAEndpoints.scoreboard_today()
    assert url == "https://cdn.nba.com/static/json/liveData/scoreboard/todaysScoreboard_00.json"


def test_scoreboard_date():
    url = NBAEndpoints.scoreboard("2026-04-12")
    assert url == "https://stats.nba.com/stats/scoreboardv3?GameDate=2026-04-12&LeagueID=00"


def test_boxscore():
    url = NBAEndpoints.boxscore("0022501186")
    assert url == "https://cdn.nba.com/static/json/liveData/boxscore/boxscore_0022501186.json"


def test_playbyplay():
    url = NBAEndpoints.playbyplay("0022501186")
    assert url == "https://cdn.nba.com/static/json/liveData/playbyplay/playbyplay_0022501186.json"


def test_standings():
    url = NBAEndpoints.standings("2025-26")
    assert "Season=2025-26" in url
    assert "SeasonType=Regular+Season" in url


def test_player_stats():
    url = NBAEndpoints.player_stats("2025-26")
    assert "Season=2025-26" in url
    assert "PerMode=PerGame" in url


def test_team_stats():
    url = NBAEndpoints.team_stats("2025-26")
    assert "Season=2025-26" in url
    assert "PerMode=PerGame" in url


def test_stats_headers():
    headers = NBAEndpoints.stats_headers()
    assert "User-Agent" in headers
    assert "Referer" in headers
