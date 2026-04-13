# NBA Data Layer (`nba_api`) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a shared Python data layer that wraps NBA API endpoints, returning clean dataclasses for scoreboard, box scores, play-by-play, standings, and player/team stats — with caching, date navigation, and live polling.

**Architecture:** A `nba_api` package with four modules: `models.py` (dataclasses), `endpoints.py` (URL construction), `client.py` (fetching, caching, polling), and `date_utils.py` (date parsing/navigation). The client returns model objects only — no raw JSON leaks to consumers.

**Tech Stack:** Python 3, `requests`, `pytz`, `dataclasses` (stdlib)

---

## Endpoint Reference

These are the verified NBA API endpoints and their response shapes (researched 2026-04-13):

| Endpoint | URL Pattern | Auth | Notes |
|----------|------------|------|-------|
| Scoreboard (today) | `https://cdn.nba.com/static/json/liveData/scoreboard/todaysScoreboard_00.json` | None | CDN, fast |
| Scoreboard (any date) | `https://stats.nba.com/stats/scoreboardv3?GameDate={YYYY-MM-DD}&LeagueID=00` | Headers* | Same response shape as CDN |
| Box Score | `https://cdn.nba.com/static/json/liveData/boxscore/boxscore_{gameId}.json` | None | CDN |
| Play-by-Play | `https://cdn.nba.com/static/json/liveData/playbyplay/playbyplay_{gameId}.json` | None | CDN |
| Standings | `https://stats.nba.com/stats/leaguestandingsv3?LeagueID=00&Season={YYYY-YY}&SeasonType=Regular+Season` | Headers* | `resultSets` format |
| Player Stats | `https://stats.nba.com/stats/leaguedashplayerstats?...Season={YYYY-YY}&SeasonType=Regular+Season&PerMode=PerGame` | Headers* | `resultSets` format |
| Team Stats | `https://stats.nba.com/stats/leaguedashteamstats?...Season={YYYY-YY}&SeasonType=Regular+Season&PerMode=PerGame` | Headers* | `resultSets` format |

*Headers required for stats.nba.com:
```python
{
    "User-Agent": "Mozilla/5.0",
    "Referer": "https://www.nba.com/",
    "Accept": "application/json"
}
```

---

### Task 1: Project Setup and Data Models

**Files:**
- Create: `nba_api/__init__.py`
- Create: `nba_api/models.py`
- Create: `tests/__init__.py`
- Create: `tests/test_models.py`
- Create: `requirements.txt`

- [ ] **Step 1: Create package structure**

```bash
mkdir -p nba_api tests
touch nba_api/__init__.py tests/__init__.py
```

- [ ] **Step 2: Create requirements.txt**

Create `requirements.txt`:
```
requests>=2.28.0
pytz>=2023.3
textual>=0.47.0
PySide6>=6.6.0
pytest>=7.0.0
```

- [ ] **Step 3: Install dependencies**

```bash
pip install -r requirements.txt
```

- [ ] **Step 4: Write failing tests for Team model**

Create `tests/test_models.py`:
```python
from nba_api.models import Team, PeriodScore


def test_team_basic_fields():
    team = Team(
        team_id=1610612738,
        name="Celtics",
        city="Boston",
        tricode="BOS",
        slug="celtics",
        wins=56,
        losses=26,
        score=113,
    )
    assert team.name == "Celtics"
    assert team.tricode == "BOS"
    assert team.record == "56-26"


def test_team_with_periods():
    team = Team(
        team_id=1610612738,
        name="Celtics",
        city="Boston",
        tricode="BOS",
        slug="celtics",
        wins=56,
        losses=26,
        score=113,
        periods=[
            PeriodScore(period=1, period_type="REGULAR", score=20),
            PeriodScore(period=2, period_type="REGULAR", score=32),
        ],
    )
    assert len(team.periods) == 2
    assert team.periods[0].score == 20
```

- [ ] **Step 5: Run tests to verify they fail**

```bash
pytest tests/test_models.py -v
```
Expected: FAIL — `ModuleNotFoundError: No module named 'nba_api.models'`

- [ ] **Step 6: Implement Team and PeriodScore models**

Create `nba_api/models.py`:
```python
from dataclasses import dataclass, field


@dataclass
class PeriodScore:
    period: int
    period_type: str
    score: int


@dataclass
class Team:
    team_id: int
    name: str
    city: str
    tricode: str
    slug: str
    wins: int
    losses: int
    score: int
    periods: list[PeriodScore] = field(default_factory=list)

    @property
    def record(self) -> str:
        return f"{self.wins}-{self.losses}"
```

- [ ] **Step 7: Run tests to verify they pass**

```bash
pytest tests/test_models.py -v
```
Expected: 2 passed

- [ ] **Step 8: Write failing tests for GameLeader and Game models**

Append to `tests/test_models.py`:
```python
from nba_api.models import Team, PeriodScore, GameLeader, Game


def test_game_leader():
    leader = GameLeader(
        person_id=1631248,
        name="Baylor Scheierman",
        jersey_num="55",
        position="G",
        team_tricode="BOS",
        points=30,
        rebounds=7,
        assists=7,
    )
    assert leader.name == "Baylor Scheierman"
    assert leader.points == 30


def _make_team(name="Celtics", tricode="BOS", score=113, wins=56, losses=26):
    return Team(
        team_id=1,
        name=name,
        city="Boston",
        tricode=tricode,
        slug=name.lower(),
        wins=wins,
        losses=losses,
        score=score,
    )


def test_game_scheduled():
    game = Game(
        game_id="0022501186",
        game_code="20260412/ORLBOS",
        status=1,
        status_text="7:00 pm ET",
        period=0,
        game_clock="",
        game_time_utc="2026-04-12T23:00:00Z",
        game_et="2026-04-12T19:00:00Z",
        home_team=_make_team(),
        away_team=_make_team("Magic", "ORL", 0, 45, 37),
    )
    assert game.is_scheduled
    assert not game.is_live
    assert not game.is_final


def test_game_live():
    game = Game(
        game_id="0022501186",
        game_code="20260412/ORLBOS",
        status=2,
        status_text="Q3 5:42",
        period=3,
        game_clock="PT05M42.00S",
        game_time_utc="2026-04-12T23:00:00Z",
        game_et="2026-04-12T19:00:00Z",
        home_team=_make_team(score=78),
        away_team=_make_team("Magic", "ORL", 72, 45, 37),
    )
    assert game.is_live
    assert not game.is_scheduled
    assert not game.is_final


def test_game_final():
    game = Game(
        game_id="0022501186",
        game_code="20260412/ORLBOS",
        status=3,
        status_text="Final",
        period=4,
        game_clock="",
        game_time_utc="2026-04-12T23:00:00Z",
        game_et="2026-04-12T19:00:00Z",
        home_team=_make_team(score=113),
        away_team=_make_team("Magic", "ORL", 108, 45, 37),
    )
    assert game.is_final
    assert not game.is_live


def test_game_overtime():
    game = Game(
        game_id="0022501186",
        game_code="20260412/ORLBOS",
        status=3,
        status_text="Final/OT",
        period=5,
        game_clock="",
        game_time_utc="2026-04-12T23:00:00Z",
        game_et="2026-04-12T19:00:00Z",
        regulation_periods=4,
        home_team=_make_team(score=120),
        away_team=_make_team("Magic", "ORL", 118, 45, 37),
    )
    assert game.is_final
    assert game.overtime_periods == 1
```

- [ ] **Step 9: Run tests to verify they fail**

```bash
pytest tests/test_models.py -v
```
Expected: FAIL — `ImportError: cannot import name 'GameLeader'`

- [ ] **Step 10: Implement GameLeader and Game models**

Append to `nba_api/models.py`:
```python
from typing import Optional


@dataclass
class GameLeader:
    person_id: int
    name: str
    jersey_num: str
    position: str
    team_tricode: str
    points: int
    rebounds: int
    assists: int


@dataclass
class Game:
    game_id: str
    game_code: str
    status: int  # 1=scheduled, 2=live, 3=final
    status_text: str
    period: int
    game_clock: str
    game_time_utc: str
    game_et: str
    home_team: Team
    away_team: Team
    regulation_periods: int = 4
    home_leader: Optional[GameLeader] = None
    away_leader: Optional[GameLeader] = None

    @property
    def is_scheduled(self) -> bool:
        return self.status == 1

    @property
    def is_live(self) -> bool:
        return self.status == 2

    @property
    def is_final(self) -> bool:
        return self.status == 3

    @property
    def overtime_periods(self) -> int:
        return max(0, self.period - self.regulation_periods)
```

Note: update the imports at the top of `nba_api/models.py` to include `Optional`:
```python
from dataclasses import dataclass, field
from typing import Optional
```

- [ ] **Step 11: Run tests to verify they pass**

```bash
pytest tests/test_models.py -v
```
Expected: 6 passed

- [ ] **Step 12: Write failing tests for BoxScore models**

Append to `tests/test_models.py`:
```python
from nba_api.models import PlayerBoxScore, TeamBoxScore


def test_player_box_score():
    player = PlayerBoxScore(
        person_id=1631248,
        name="Baylor Scheierman",
        name_short="B. Scheierman",
        jersey_num="55",
        position="SF",
        starter=True,
        minutes="PT38M48.40S",
        points=30,
        rebounds=7,
        assists=7,
        steals=2,
        blocks=1,
        turnovers=3,
        fouls=3,
        fg_made=8,
        fg_attempted=20,
        fg_pct=0.4,
        fg3_made=6,
        fg3_attempted=14,
        fg3_pct=0.429,
        ft_made=8,
        ft_attempted=8,
        ft_pct=1.0,
        plus_minus=15.0,
        reb_offensive=0,
        reb_defensive=7,
    )
    assert player.name == "Baylor Scheierman"
    assert player.starter is True
    assert player.points == 30
    assert player.minutes_display == "38:48"


def test_team_box_score():
    box = TeamBoxScore(
        team=_make_team(),
        players=[],
        total_points=113,
        total_rebounds=50,
        total_assists=24,
        total_steals=10,
        total_blocks=6,
        total_turnovers=17,
        total_fouls=23,
        fg_made=36,
        fg_attempted=87,
        fg_pct=0.414,
        fg3_made=19,
        fg3_attempted=50,
        fg3_pct=0.38,
        ft_made=22,
        ft_attempted=22,
        ft_pct=1.0,
        points_in_paint=32,
        points_fastbreak=18,
        points_second_chance=11,
        bench_points=17,
        biggest_lead=16,
    )
    assert box.total_points == 113
    assert box.bench_points == 17
```

- [ ] **Step 13: Run tests to verify they fail**

```bash
pytest tests/test_models.py -v
```
Expected: FAIL — `ImportError: cannot import name 'PlayerBoxScore'`

- [ ] **Step 14: Implement BoxScore models**

Append to `nba_api/models.py`:
```python
import re


@dataclass
class PlayerBoxScore:
    person_id: int
    name: str
    name_short: str
    jersey_num: str
    position: str
    starter: bool
    minutes: str  # ISO duration "PT38M48.40S"
    points: int
    rebounds: int
    assists: int
    steals: int
    blocks: int
    turnovers: int
    fouls: int
    fg_made: int
    fg_attempted: int
    fg_pct: float
    fg3_made: int
    fg3_attempted: int
    fg3_pct: float
    ft_made: int
    ft_attempted: int
    ft_pct: float
    plus_minus: float
    reb_offensive: int
    reb_defensive: int

    @property
    def minutes_display(self) -> str:
        """Convert 'PT38M48.40S' to '38:48'."""
        match = re.match(r"PT(\d+)M([\d.]+)S", self.minutes)
        if match:
            mins = int(match.group(1))
            secs = int(float(match.group(2)))
            return f"{mins}:{secs:02d}"
        return self.minutes


@dataclass
class TeamBoxScore:
    team: Team
    players: list[PlayerBoxScore]
    total_points: int
    total_rebounds: int
    total_assists: int
    total_steals: int
    total_blocks: int
    total_turnovers: int
    total_fouls: int
    fg_made: int
    fg_attempted: int
    fg_pct: float
    fg3_made: int
    fg3_attempted: int
    fg3_pct: float
    ft_made: int
    ft_attempted: int
    ft_pct: float
    points_in_paint: int
    points_fastbreak: int
    points_second_chance: int
    bench_points: int
    biggest_lead: int
```

Note: add `import re` at the top of `nba_api/models.py`.

- [ ] **Step 15: Run tests to verify they pass**

```bash
pytest tests/test_models.py -v
```
Expected: 8 passed

- [ ] **Step 16: Write failing tests for PlayByPlay and remaining models**

Append to `tests/test_models.py`:
```python
from nba_api.models import PlayAction, StandingsEntry, PlayerStats, TeamStats


def test_play_action():
    action = PlayAction(
        action_number=4,
        clock="PT11M57.00S",
        period=1,
        period_type="REGULAR",
        action_type="jumpball",
        description="Jump Ball W. Carter Jr. vs. L. Garza: Tip to P. Banchero",
        team_tricode="ORL",
        person_id=1631094,
        player_name="Banchero",
        score_home="0",
        score_away="0",
        is_field_goal=False,
    )
    assert action.description.startswith("Jump Ball")
    assert action.period == 1


def test_standings_entry():
    entry = StandingsEntry(
        team_id=1610612760,
        team_name="Thunder",
        team_city="Oklahoma City",
        team_tricode="OKC",
        conference="West",
        division="Northwest",
        division_rank=1,
        playoff_rank=1,
        wins=64,
        losses=18,
        win_pct=0.78,
        home_record="34-7",
        road_record="30-10",
        last_10="7-3",
        streak="L 2",
        games_back=0.0,
        clinch_indicator=" - w",
    )
    assert entry.team_name == "Thunder"
    assert entry.record == "64-18"


def test_player_stats():
    stats = PlayerStats(
        player_id=203999,
        player_name="Nikola Jokic",
        team_id=1610612743,
        team_abbreviation="DEN",
        age=31.0,
        gp=79,
        mpg=36.5,
        ppg=30.2,
        rpg=13.1,
        apg=10.5,
        spg=1.7,
        bpg=0.8,
        topg=3.8,
        fpg=2.6,
        fg_pct=0.580,
        fg3_pct=0.410,
        ft_pct=0.830,
        plus_minus=8.5,
    )
    assert stats.player_name == "Nikola Jokic"
    assert stats.ppg == 30.2


def test_team_stats():
    stats = TeamStats(
        team_id=1610612737,
        team_name="Atlanta Hawks",
        gp=82,
        wins=46,
        losses=36,
        win_pct=0.561,
        mpg=48.2,
        ppg=118.5,
        rpg=43.5,
        apg=30.1,
        spg=9.4,
        bpg=4.7,
        topg=14.2,
        fpg=19.7,
        fg_pct=0.474,
        fg3_pct=0.371,
        ft_pct=0.774,
        plus_minus=2.4,
    )
    assert stats.team_name == "Atlanta Hawks"
    assert stats.ppg == 118.5
```

- [ ] **Step 17: Run tests to verify they fail**

```bash
pytest tests/test_models.py -v
```
Expected: FAIL — `ImportError: cannot import name 'PlayAction'`

- [ ] **Step 18: Implement remaining models**

Append to `nba_api/models.py`:
```python
@dataclass
class PlayAction:
    action_number: int
    clock: str
    period: int
    period_type: str
    action_type: str
    description: str
    team_tricode: str
    person_id: int
    player_name: str
    score_home: str
    score_away: str
    is_field_goal: bool


@dataclass
class StandingsEntry:
    team_id: int
    team_name: str
    team_city: str
    team_tricode: str
    conference: str
    division: str
    division_rank: int
    playoff_rank: int
    wins: int
    losses: int
    win_pct: float
    home_record: str
    road_record: str
    last_10: str
    streak: str
    games_back: float
    clinch_indicator: str

    @property
    def record(self) -> str:
        return f"{self.wins}-{self.losses}"


@dataclass
class PlayerStats:
    player_id: int
    player_name: str
    team_id: int
    team_abbreviation: str
    age: float
    gp: int
    mpg: float
    ppg: float
    rpg: float
    apg: float
    spg: float
    bpg: float
    topg: float
    fpg: float
    fg_pct: float
    fg3_pct: float
    ft_pct: float
    plus_minus: float


@dataclass
class TeamStats:
    team_id: int
    team_name: str
    gp: int
    wins: int
    losses: int
    win_pct: float
    mpg: float
    ppg: float
    rpg: float
    apg: float
    spg: float
    bpg: float
    topg: float
    fpg: float
    fg_pct: float
    fg3_pct: float
    ft_pct: float
    plus_minus: float
```

- [ ] **Step 19: Run tests to verify they pass**

```bash
pytest tests/test_models.py -v
```
Expected: 12 passed

- [ ] **Step 20: Commit**

```bash
git add nba_api/ tests/ requirements.txt
git commit -m "feat: add nba_api data models with full test coverage"
```

---

### Task 2: Endpoints Module

**Files:**
- Create: `nba_api/endpoints.py`
- Create: `tests/test_endpoints.py`

- [ ] **Step 1: Write failing tests for endpoint URL construction**

Create `tests/test_endpoints.py`:
```python
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
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_endpoints.py -v
```
Expected: FAIL — `ModuleNotFoundError: No module named 'nba_api.endpoints'`

- [ ] **Step 3: Implement endpoints module**

Create `nba_api/endpoints.py`:
```python
class NBAEndpoints:
    _CDN_BASE = "https://cdn.nba.com/static/json/liveData"
    _STATS_BASE = "https://stats.nba.com/stats"

    @staticmethod
    def scoreboard_today() -> str:
        return f"{NBAEndpoints._CDN_BASE}/scoreboard/todaysScoreboard_00.json"

    @staticmethod
    def scoreboard(game_date: str) -> str:
        return f"{NBAEndpoints._STATS_BASE}/scoreboardv3?GameDate={game_date}&LeagueID=00"

    @staticmethod
    def boxscore(game_id: str) -> str:
        return f"{NBAEndpoints._CDN_BASE}/boxscore/boxscore_{game_id}.json"

    @staticmethod
    def playbyplay(game_id: str) -> str:
        return f"{NBAEndpoints._CDN_BASE}/playbyplay/playbyplay_{game_id}.json"

    @staticmethod
    def standings(season: str) -> str:
        return (
            f"{NBAEndpoints._STATS_BASE}/leaguestandingsv3"
            f"?LeagueID=00&Season={season}&SeasonType=Regular+Season"
        )

    @staticmethod
    def player_stats(season: str) -> str:
        return (
            f"{NBAEndpoints._STATS_BASE}/leaguedashplayerstats"
            f"?College=&Conference=&Country=&DateFrom=&DateTo="
            f"&Division=&DraftPick=&DraftYear=&GameScope="
            f"&GameSegment=&Height=&ISTRound=&LastNGames=0"
            f"&LeagueID=00&Location=&MeasureType=Base&Month=0"
            f"&OpponentTeamID=0&Outcome=&PORound=0&PaceAdjust=N"
            f"&PerMode=PerGame&Period=0&PlayerExperience="
            f"&PlayerPosition=&PlusMinus=N&Rank=N&Season={season}"
            f"&SeasonSegment=&SeasonType=Regular+Season"
            f"&ShotClockRange=&StarterBench=&TeamID=0"
            f"&VsConference=&VsDivision=&Weight="
        )

    @staticmethod
    def team_stats(season: str) -> str:
        return (
            f"{NBAEndpoints._STATS_BASE}/leaguedashteamstats"
            f"?Conference=&DateFrom=&DateTo=&Division=&GameScope="
            f"&GameSegment=&Height=&ISTRound=&LastNGames=0"
            f"&LeagueID=00&Location=&MeasureType=Base&Month=0"
            f"&OpponentTeamID=0&Outcome=&PORound=0&PaceAdjust=N"
            f"&PerMode=PerGame&Period=0&PlayerExperience="
            f"&PlayerPosition=&PlusMinus=N&Rank=N&Season={season}"
            f"&SeasonSegment=&SeasonType=Regular+Season"
            f"&ShotClockRange=&StarterBench=&TeamID=0"
            f"&VsConference=&VsDivision="
        )

    @staticmethod
    def stats_headers() -> dict[str, str]:
        return {
            "User-Agent": "Mozilla/5.0",
            "Referer": "https://www.nba.com/",
            "Accept": "application/json",
        }
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_endpoints.py -v
```
Expected: 8 passed

- [ ] **Step 5: Commit**

```bash
git add nba_api/endpoints.py tests/test_endpoints.py
git commit -m "feat: add NBA endpoint URL construction"
```

---

### Task 3: Date Utilities

**Files:**
- Create: `nba_api/date_utils.py`
- Create: `tests/test_date_utils.py`

- [ ] **Step 1: Write failing tests for date parsing**

Create `tests/test_date_utils.py`:
```python
from datetime import date
from nba_api.date_utils import parse_game_date, next_day, prev_day, game_date_to_season


def test_parse_today(monkeypatch):
    monkeypatch.setattr("nba_api.date_utils.date", type("MockDate", (), {
        "today": staticmethod(lambda: date(2026, 4, 13)),
        "__call__": date.__call__,
    }))
    # Simpler: just test with explicit dates
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
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_date_utils.py -v
```
Expected: FAIL — `ModuleNotFoundError`

- [ ] **Step 3: Implement date utilities**

Create `nba_api/date_utils.py`:
```python
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
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest tests/test_date_utils.py -v
```
Expected: 8 passed

- [ ] **Step 5: Commit**

```bash
git add nba_api/date_utils.py tests/test_date_utils.py
git commit -m "feat: add date parsing and season calculation utilities"
```

---

### Task 4: API Client — JSON Parsing (Scoreboard)

**Files:**
- Create: `nba_api/client.py`
- Create: `tests/test_client.py`
- Create: `tests/fixtures/scoreboard_20260412.json`

This task implements the JSON→model parsing. We test with fixture files so tests don't hit the network.

- [ ] **Step 1: Create scoreboard fixture**

Save the real API response for April 12, 2026 as a test fixture:

```bash
python3 -c "
import requests, json
headers = {'User-Agent': 'Mozilla/5.0', 'Referer': 'https://www.nba.com/', 'Accept': 'application/json'}
url = 'https://stats.nba.com/stats/scoreboardv3?GameDate=2026-04-12&LeagueID=00'
r = requests.get(url, headers=headers, timeout=10)
with open('tests/fixtures/scoreboard_20260412.json', 'w') as f:
    json.dump(r.json(), f, indent=2)
print('Saved fixture')
"
```

Also create the fixtures directory:
```bash
mkdir -p tests/fixtures
```

- [ ] **Step 2: Write failing tests for scoreboard parsing**

Create `tests/test_client.py`:
```python
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
```

- [ ] **Step 3: Run tests to verify they fail**

```bash
pytest tests/test_client.py -v
```
Expected: FAIL — `ImportError: cannot import name 'NBAClient'`

- [ ] **Step 4: Implement NBAClient with scoreboard parsing**

Create `nba_api/client.py`:
```python
import requests
from typing import Optional
from nba_api.endpoints import NBAEndpoints
from nba_api.models import (
    Team, PeriodScore, GameLeader, Game,
    PlayerBoxScore, TeamBoxScore, PlayAction,
    StandingsEntry, PlayerStats, TeamStats,
)

REQUEST_TIMEOUT = 5


class NBAClient:
    def __init__(self):
        self._session = requests.Session()
        self._session.headers.update(NBAEndpoints.stats_headers())

    def _get(self, url: str) -> dict:
        response = self._session.get(url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.json()

    def _parse_team(self, data: dict) -> Team:
        periods = [
            PeriodScore(
                period=p["period"],
                period_type=p["periodType"],
                score=p["score"],
            )
            for p in data.get("periods", [])
        ]
        return Team(
            team_id=data["teamId"],
            name=data["teamName"],
            city=data["teamCity"],
            tricode=data["teamTricode"],
            slug=data.get("teamSlug", ""),
            wins=data.get("wins", 0),
            losses=data.get("losses", 0),
            score=data.get("score", 0),
            periods=periods,
        )

    def _parse_leader(self, data: dict) -> Optional[GameLeader]:
        if not data or not data.get("name"):
            return None
        return GameLeader(
            person_id=data["personId"],
            name=data["name"],
            jersey_num=data.get("jerseyNum", ""),
            position=data.get("position", ""),
            team_tricode=data.get("teamTricode", ""),
            points=data.get("points", 0),
            rebounds=data.get("rebounds", 0),
            assists=data.get("assists", 0),
        )

    def _parse_scoreboard(self, raw: dict) -> list[Game]:
        games_data = raw.get("scoreboard", {}).get("games", [])
        games = []
        for g in games_data:
            leaders = g.get("gameLeaders", {})
            games.append(Game(
                game_id=g["gameId"],
                game_code=g["gameCode"],
                status=g["gameStatus"],
                status_text=g["gameStatusText"],
                period=g.get("period", 0),
                game_clock=g.get("gameClock", ""),
                game_time_utc=g.get("gameTimeUTC", ""),
                game_et=g.get("gameEt", ""),
                regulation_periods=g.get("regulationPeriods", 4),
                home_team=self._parse_team(g["homeTeam"]),
                away_team=self._parse_team(g["awayTeam"]),
                home_leader=self._parse_leader(leaders.get("homeLeaders")),
                away_leader=self._parse_leader(leaders.get("awayLeaders")),
            ))
        return games
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
pytest tests/test_client.py -v
```
Expected: 2 passed

- [ ] **Step 6: Commit**

```bash
git add nba_api/client.py tests/test_client.py tests/fixtures/
git commit -m "feat: add NBAClient with scoreboard JSON parsing"
```

---

### Task 5: API Client — Box Score and Play-by-Play Parsing

**Files:**
- Modify: `nba_api/client.py`
- Modify: `tests/test_client.py`
- Create: `tests/fixtures/boxscore_0022501186.json`
- Create: `tests/fixtures/playbyplay_0022501186.json`

- [ ] **Step 1: Create box score and play-by-play fixtures**

```bash
python3 -c "
import requests, json
headers = {'User-Agent': 'Mozilla/5.0', 'Referer': 'https://www.nba.com/', 'Accept': 'application/json'}

# Box score
url = 'https://cdn.nba.com/static/json/liveData/boxscore/boxscore_0022501186.json'
r = requests.get(url, headers=headers, timeout=10)
with open('tests/fixtures/boxscore_0022501186.json', 'w') as f:
    json.dump(r.json(), f, indent=2)

# Play-by-play
url = 'https://cdn.nba.com/static/json/liveData/playbyplay/playbyplay_0022501186.json'
r = requests.get(url, headers=headers, timeout=10)
with open('tests/fixtures/playbyplay_0022501186.json', 'w') as f:
    json.dump(r.json(), f, indent=2)

print('Saved box score and play-by-play fixtures')
"
```

- [ ] **Step 2: Write failing tests for box score parsing**

Append to `tests/test_client.py`:
```python
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
```

- [ ] **Step 3: Run tests to verify they fail**

```bash
pytest tests/test_client.py::test_parse_boxscore -v
```
Expected: FAIL — `AttributeError: 'NBAClient' object has no attribute '_parse_boxscore'`

- [ ] **Step 4: Implement box score parsing**

Append these methods to the `NBAClient` class in `nba_api/client.py`:
```python
    def _parse_player_boxscore(self, data: dict) -> PlayerBoxScore:
        stats = data.get("statistics", {})
        return PlayerBoxScore(
            person_id=data["personId"],
            name=data.get("name", ""),
            name_short=data.get("nameI", ""),
            jersey_num=data.get("jerseyNum", ""),
            position=data.get("position", ""),
            starter=data.get("starter", "0") == "1",
            minutes=stats.get("minutes", "PT00M00.00S"),
            points=stats.get("points", 0),
            rebounds=stats.get("reboundsTotal", 0),
            assists=stats.get("assists", 0),
            steals=stats.get("steals", 0),
            blocks=stats.get("blocks", 0),
            turnovers=stats.get("turnovers", 0),
            fouls=stats.get("foulsPersonal", 0),
            fg_made=stats.get("fieldGoalsMade", 0),
            fg_attempted=stats.get("fieldGoalsAttempted", 0),
            fg_pct=stats.get("fieldGoalsPercentage", 0.0),
            fg3_made=stats.get("threePointersMade", 0),
            fg3_attempted=stats.get("threePointersAttempted", 0),
            fg3_pct=stats.get("threePointersPercentage", 0.0),
            ft_made=stats.get("freeThrowsMade", 0),
            ft_attempted=stats.get("freeThrowsAttempted", 0),
            ft_pct=stats.get("freeThrowsPercentage", 0.0),
            plus_minus=stats.get("plusMinusPoints", 0.0),
            reb_offensive=stats.get("reboundsOffensive", 0),
            reb_defensive=stats.get("reboundsDefensive", 0),
        )

    def _parse_team_boxscore(self, team_data: dict) -> TeamBoxScore:
        players = [
            self._parse_player_boxscore(p)
            for p in team_data.get("players", [])
            if p.get("played", "0") == "1"
        ]
        stats = team_data.get("statistics", {})
        return TeamBoxScore(
            team=self._parse_team(team_data),
            players=players,
            total_points=stats.get("points", 0),
            total_rebounds=stats.get("reboundsTotal", 0),
            total_assists=stats.get("assists", 0),
            total_steals=stats.get("steals", 0),
            total_blocks=stats.get("blocks", 0),
            total_turnovers=stats.get("turnoversTotal", 0),
            total_fouls=stats.get("foulsPersonal", 0),
            fg_made=stats.get("fieldGoalsMade", 0),
            fg_attempted=stats.get("fieldGoalsAttempted", 0),
            fg_pct=stats.get("fieldGoalsPercentage", 0.0),
            fg3_made=stats.get("threePointersMade", 0),
            fg3_attempted=stats.get("threePointersAttempted", 0),
            fg3_pct=stats.get("threePointersPercentage", 0.0),
            ft_made=stats.get("freeThrowsMade", 0),
            ft_attempted=stats.get("freeThrowsAttempted", 0),
            ft_pct=stats.get("freeThrowsPercentage", 0.0),
            points_in_paint=stats.get("pointsInThePaint", 0),
            points_fastbreak=stats.get("pointsFastBreak", 0),
            points_second_chance=stats.get("pointsSecondChance", 0),
            bench_points=stats.get("benchPoints", 0),
            biggest_lead=stats.get("biggestLead", 0),
        )

    def _parse_boxscore(self, raw: dict) -> tuple[TeamBoxScore, TeamBoxScore]:
        game = raw.get("game", {})
        home = self._parse_team_boxscore(game["homeTeam"])
        away = self._parse_team_boxscore(game["awayTeam"])
        return home, away
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
pytest tests/test_client.py -v
```
Expected: 3 passed

- [ ] **Step 6: Write failing test for play-by-play parsing**

Append to `tests/test_client.py`:
```python
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
```

- [ ] **Step 7: Run test to verify it fails**

```bash
pytest tests/test_client.py::test_parse_playbyplay -v
```
Expected: FAIL — `AttributeError: 'NBAClient' object has no attribute '_parse_playbyplay'`

- [ ] **Step 8: Implement play-by-play parsing**

Append this method to the `NBAClient` class in `nba_api/client.py`:
```python
    def _parse_playbyplay(self, raw: dict) -> list[PlayAction]:
        actions_data = raw.get("game", {}).get("actions", [])
        actions = []
        for a in actions_data:
            actions.append(PlayAction(
                action_number=a.get("actionNumber", 0),
                clock=a.get("clock", ""),
                period=a.get("period", 0),
                period_type=a.get("periodType", "REGULAR"),
                action_type=a.get("actionType", ""),
                description=a.get("description", ""),
                team_tricode=a.get("teamTricode", ""),
                person_id=a.get("personId", 0),
                player_name=a.get("playerName", ""),
                score_home=a.get("scoreHome", "0"),
                score_away=a.get("scoreAway", "0"),
                is_field_goal=bool(a.get("isFieldGoal", 0)),
            ))
        return actions
```

- [ ] **Step 9: Run tests to verify they pass**

```bash
pytest tests/test_client.py -v
```
Expected: 4 passed

- [ ] **Step 10: Commit**

```bash
git add nba_api/client.py tests/test_client.py tests/fixtures/
git commit -m "feat: add box score and play-by-play parsing"
```

---

### Task 6: API Client — Standings and Stats Parsing

**Files:**
- Modify: `nba_api/client.py`
- Modify: `tests/test_client.py`
- Create: `tests/fixtures/standings_2025-26.json`
- Create: `tests/fixtures/player_stats_2025-26.json`
- Create: `tests/fixtures/team_stats_2025-26.json`

- [ ] **Step 1: Create standings and stats fixtures**

```bash
python3 -c "
import requests, json
headers = {'User-Agent': 'Mozilla/5.0', 'Referer': 'https://www.nba.com/', 'Accept': 'application/json'}

# Standings
url = 'https://stats.nba.com/stats/leaguestandingsv3?LeagueID=00&Season=2025-26&SeasonType=Regular+Season'
r = requests.get(url, headers=headers, timeout=10)
with open('tests/fixtures/standings_2025-26.json', 'w') as f:
    json.dump(r.json(), f, indent=2)

# Player stats
url = 'https://stats.nba.com/stats/leaguedashplayerstats?College=&Conference=&Country=&DateFrom=&DateTo=&Division=&DraftPick=&DraftYear=&GameScope=&GameSegment=&Height=&ISTRound=&LastNGames=0&LeagueID=00&Location=&MeasureType=Base&Month=0&OpponentTeamID=0&Outcome=&PORound=0&PaceAdjust=N&PerMode=PerGame&Period=0&PlayerExperience=&PlayerPosition=&PlusMinus=N&Rank=N&Season=2025-26&SeasonSegment=&SeasonType=Regular+Season&ShotClockRange=&StarterBench=&TeamID=0&VsConference=&VsDivision=&Weight='
r = requests.get(url, headers=headers, timeout=10)
with open('tests/fixtures/player_stats_2025-26.json', 'w') as f:
    json.dump(r.json(), f, indent=2)

# Team stats
url = 'https://stats.nba.com/stats/leaguedashteamstats?Conference=&DateFrom=&DateTo=&Division=&GameScope=&GameSegment=&Height=&ISTRound=&LastNGames=0&LeagueID=00&Location=&MeasureType=Base&Month=0&OpponentTeamID=0&Outcome=&PORound=0&PaceAdjust=N&PerMode=PerGame&Period=0&PlayerExperience=&PlayerPosition=&PlusMinus=N&Rank=N&Season=2025-26&SeasonSegment=&SeasonType=Regular+Season&ShotClockRange=&StarterBench=&TeamID=0&VsConference=&VsDivision='
r = requests.get(url, headers=headers, timeout=10)
with open('tests/fixtures/team_stats_2025-26.json', 'w') as f:
    json.dump(r.json(), f, indent=2)

print('Saved all fixtures')
"
```

- [ ] **Step 2: Write failing tests for standings parsing**

Append to `tests/test_client.py`:
```python
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
```

- [ ] **Step 3: Run tests to verify they fail**

```bash
pytest tests/test_client.py::test_parse_standings tests/test_client.py::test_parse_player_stats tests/test_client.py::test_parse_team_stats -v
```
Expected: FAIL — `AttributeError: 'NBAClient' object has no attribute '_parse_standings'`

- [ ] **Step 4: Implement standings parsing**

Append these methods to the `NBAClient` class in `nba_api/client.py`:
```python
    def _parse_standings(self, raw: dict) -> list[StandingsEntry]:
        result_sets = raw.get("resultSets", [])
        if not result_sets:
            return []
        headers = result_sets[0].get("headers", [])
        rows = result_sets[0].get("rowSet", [])

        def col(row, name):
            try:
                return row[headers.index(name)]
            except (ValueError, IndexError):
                return None

        entries = []
        for row in rows:
            entries.append(StandingsEntry(
                team_id=col(row, "TeamID"),
                team_name=col(row, "TeamName"),
                team_city=col(row, "TeamCity"),
                team_tricode=col(row, "TeamSlug"),  # slug is closest; tricode not in standings
                conference=col(row, "Conference"),
                division=col(row, "Division"),
                division_rank=col(row, "DivisionRank") or 0,
                playoff_rank=col(row, "PlayoffRank") or 0,
                wins=col(row, "WINS") or 0,
                losses=col(row, "LOSSES") or 0,
                win_pct=col(row, "WinPCT") or 0.0,
                home_record=col(row, "HOME") or "",
                road_record=col(row, "ROAD") or "",
                last_10=col(row, "L10") or "",
                streak=col(row, "strCurrentStreak") or "",
                games_back=col(row, "ConferenceGamesBack") or 0.0,
                clinch_indicator=col(row, "ClinchIndicator") or "",
            ))
        return entries

    def _parse_player_stats(self, raw: dict) -> list[PlayerStats]:
        result_sets = raw.get("resultSets", [])
        if not result_sets:
            return []
        headers = result_sets[0].get("headers", [])
        rows = result_sets[0].get("rowSet", [])

        def col(row, name):
            try:
                return row[headers.index(name)]
            except (ValueError, IndexError):
                return None

        stats = []
        for row in rows:
            stats.append(PlayerStats(
                player_id=col(row, "PLAYER_ID"),
                player_name=col(row, "PLAYER_NAME") or "",
                team_id=col(row, "TEAM_ID") or 0,
                team_abbreviation=col(row, "TEAM_ABBREVIATION") or "",
                age=col(row, "AGE") or 0.0,
                gp=col(row, "GP") or 0,
                mpg=col(row, "MIN") or 0.0,
                ppg=col(row, "PTS") or 0.0,
                rpg=col(row, "REB") or 0.0,
                apg=col(row, "AST") or 0.0,
                spg=col(row, "STL") or 0.0,
                bpg=col(row, "BLK") or 0.0,
                topg=col(row, "TOV") or 0.0,
                fpg=col(row, "PF") or 0.0,
                fg_pct=col(row, "FG_PCT") or 0.0,
                fg3_pct=col(row, "FG3_PCT") or 0.0,
                ft_pct=col(row, "FT_PCT") or 0.0,
                plus_minus=col(row, "PLUS_MINUS") or 0.0,
            ))
        return stats

    def _parse_team_stats(self, raw: dict) -> list[TeamStats]:
        result_sets = raw.get("resultSets", [])
        if not result_sets:
            return []
        headers = result_sets[0].get("headers", [])
        rows = result_sets[0].get("rowSet", [])

        def col(row, name):
            try:
                return row[headers.index(name)]
            except (ValueError, IndexError):
                return None

        stats = []
        for row in rows:
            stats.append(TeamStats(
                team_id=col(row, "TEAM_ID"),
                team_name=col(row, "TEAM_NAME") or "",
                gp=col(row, "GP") or 0,
                wins=col(row, "W") or 0,
                losses=col(row, "L") or 0,
                win_pct=col(row, "W_PCT") or 0.0,
                mpg=col(row, "MIN") or 0.0,
                ppg=col(row, "PTS") or 0.0,
                rpg=col(row, "REB") or 0.0,
                apg=col(row, "AST") or 0.0,
                spg=col(row, "STL") or 0.0,
                bpg=col(row, "BLK") or 0.0,
                topg=col(row, "TOV") or 0.0,
                fpg=col(row, "PF") or 0.0,
                fg_pct=col(row, "FG_PCT") or 0.0,
                fg3_pct=col(row, "FG3_PCT") or 0.0,
                ft_pct=col(row, "FT_PCT") or 0.0,
                plus_minus=col(row, "PLUS_MINUS") or 0.0,
            ))
        return stats
```

- [ ] **Step 5: Run tests to verify they pass**

```bash
pytest tests/test_client.py -v
```
Expected: 7 passed

- [ ] **Step 6: Commit**

```bash
git add nba_api/client.py tests/test_client.py tests/fixtures/
git commit -m "feat: add standings, player stats, and team stats parsing"
```

---

### Task 7: API Client — Public Fetch Methods and Caching

**Files:**
- Modify: `nba_api/client.py`
- Modify: `tests/test_client.py`

This task adds the public API methods that fetch from the network (or return cached data) and exposes them as the interface consumers use.

- [ ] **Step 1: Write failing tests for public methods**

Append to `tests/test_client.py`:
```python
from unittest.mock import patch, MagicMock
from datetime import date


def _mock_response(fixture_name):
    with open(FIXTURES / fixture_name) as f:
        data = json.load(f)
    mock = MagicMock()
    mock.status_code = 200
    mock.json.return_value = data
    mock.raise_for_status = MagicMock()
    return mock


def test_get_scoreboard_uses_cdn_for_today():
    client = NBAClient()
    with patch.object(client._session, "get", return_value=_mock_response("scoreboard_20260412.json")) as mock_get:
        games = client.get_scoreboard(date(2026, 4, 12))
        assert len(games) > 0
        # Verify it was called
        mock_get.assert_called_once()


def test_get_scoreboard_caches_final_games():
    client = NBAClient()
    mock_resp = _mock_response("scoreboard_20260412.json")
    with patch.object(client._session, "get", return_value=mock_resp) as mock_get:
        # First call fetches
        games1 = client.get_scoreboard(date(2026, 4, 12))
        # Second call should use cache (all games are final)
        games2 = client.get_scoreboard(date(2026, 4, 12))
        assert mock_get.call_count == 1
        assert len(games1) == len(games2)


def test_get_boxscore():
    client = NBAClient()
    with patch.object(client._session, "get", return_value=_mock_response("boxscore_0022501186.json")):
        home, away = client.get_boxscore("0022501186")
        assert home.team.name == "Celtics"
        assert away.team.name == "Magic"


def test_get_playbyplay():
    client = NBAClient()
    with patch.object(client._session, "get", return_value=_mock_response("playbyplay_0022501186.json")):
        actions = client.get_playbyplay("0022501186")
        assert len(actions) > 0


def test_get_standings():
    client = NBAClient()
    with patch.object(client._session, "get", return_value=_mock_response("standings_2025-26.json")):
        entries = client.get_standings("2025-26")
        assert len(entries) == 30


def test_get_player_stats():
    client = NBAClient()
    with patch.object(client._session, "get", return_value=_mock_response("player_stats_2025-26.json")):
        stats = client.get_player_stats("2025-26")
        assert len(stats) > 100


def test_get_team_stats():
    client = NBAClient()
    with patch.object(client._session, "get", return_value=_mock_response("team_stats_2025-26.json")):
        stats = client.get_team_stats("2025-26")
        assert len(stats) == 30


def test_network_error_raises():
    client = NBAClient()
    with patch.object(client._session, "get", side_effect=requests.exceptions.Timeout("timeout")):
        try:
            client.get_scoreboard(date(2026, 4, 12))
            assert False, "Should have raised"
        except requests.exceptions.Timeout:
            pass
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest tests/test_client.py::test_get_scoreboard_uses_cdn_for_today -v
```
Expected: FAIL — `AttributeError: 'NBAClient' object has no attribute 'get_scoreboard'`

- [ ] **Step 3: Add import for requests at top of test file**

Add to the imports in `tests/test_client.py`:
```python
import requests
```

- [ ] **Step 4: Implement public fetch methods with caching**

Add these imports at the top of `nba_api/client.py`:
```python
from datetime import date
import time
from nba_api.date_utils import game_date_to_season
```

Add a cache class and update `NBAClient.__init__` and add public methods. Replace the `__init__` method and add the new methods to `nba_api/client.py`:

```python
class _Cache:
    def __init__(self):
        self._data: dict[str, tuple[float, any]] = {}

    def get(self, key: str, max_age: float) -> any:
        if key in self._data:
            ts, value = self._data[key]
            if time.time() - ts < max_age:
                return value
        return None

    def set(self, key: str, value: any) -> None:
        self._data[key] = (time.time(), value)

    def clear(self) -> None:
        self._data.clear()


CACHE_LONG = 3600  # 1 hour for completed data
CACHE_NONE = 0     # No caching for live data


class NBAClient:
    def __init__(self):
        self._session = requests.Session()
        self._session.headers.update(NBAEndpoints.stats_headers())
        self._cache = _Cache()

    # ... keep all existing _parse methods ...

    def get_scoreboard(self, game_date: date) -> list[Game]:
        key = f"scoreboard:{game_date.isoformat()}"
        cached = self._cache.get(key, CACHE_LONG)
        if cached is not None:
            return cached

        today = date.today()
        if game_date == today:
            url = NBAEndpoints.scoreboard_today()
        else:
            url = NBAEndpoints.scoreboard(game_date.isoformat())

        raw = self._get(url)
        games = self._parse_scoreboard(raw)

        # Only cache if all games are final (or no games)
        all_final = all(g.is_final or g.is_scheduled for g in games) and len(games) > 0
        no_live = not any(g.is_live for g in games)
        if all_final and no_live:
            self._cache.set(key, games)

        return games

    def get_boxscore(self, game_id: str) -> tuple[TeamBoxScore, TeamBoxScore]:
        key = f"boxscore:{game_id}"
        cached = self._cache.get(key, CACHE_LONG)
        if cached is not None:
            return cached

        raw = self._get(NBAEndpoints.boxscore(game_id))
        result = self._parse_boxscore(raw)
        self._cache.set(key, result)
        return result

    def get_playbyplay(self, game_id: str) -> list[PlayAction]:
        key = f"playbyplay:{game_id}"
        cached = self._cache.get(key, CACHE_LONG)
        if cached is not None:
            return cached

        raw = self._get(NBAEndpoints.playbyplay(game_id))
        result = self._parse_playbyplay(raw)
        self._cache.set(key, result)
        return result

    def get_standings(self, season: str) -> list[StandingsEntry]:
        key = f"standings:{season}"
        cached = self._cache.get(key, CACHE_LONG)
        if cached is not None:
            return cached

        raw = self._get(NBAEndpoints.standings(season))
        result = self._parse_standings(raw)
        self._cache.set(key, result)
        return result

    def get_player_stats(self, season: str) -> list[PlayerStats]:
        key = f"player_stats:{season}"
        cached = self._cache.get(key, CACHE_LONG)
        if cached is not None:
            return cached

        raw = self._get(NBAEndpoints.player_stats(season))
        result = self._parse_player_stats(raw)
        self._cache.set(key, result)
        return result

    def get_team_stats(self, season: str) -> list[TeamStats]:
        key = f"team_stats:{season}"
        cached = self._cache.get(key, CACHE_LONG)
        if cached is not None:
            return cached

        raw = self._get(NBAEndpoints.team_stats(season))
        result = self._parse_team_stats(raw)
        self._cache.set(key, result)
        return result
```

- [ ] **Step 5: Run all tests to verify they pass**

```bash
pytest tests/ -v
```
Expected: all tests pass (around 22 tests)

- [ ] **Step 6: Commit**

```bash
git add nba_api/client.py tests/test_client.py
git commit -m "feat: add public fetch methods with in-memory caching"
```

---

### Task 8: Package Exports and Integration Test

**Files:**
- Modify: `nba_api/__init__.py`
- Create: `tests/test_integration.py`

- [ ] **Step 1: Set up package exports**

Update `nba_api/__init__.py`:
```python
from nba_api.client import NBAClient
from nba_api.models import (
    Team, PeriodScore, GameLeader, Game,
    PlayerBoxScore, TeamBoxScore, PlayAction,
    StandingsEntry, PlayerStats, TeamStats,
)
from nba_api.date_utils import parse_game_date, next_day, prev_day, game_date_to_season
from nba_api.endpoints import NBAEndpoints

__all__ = [
    "NBAClient",
    "NBAEndpoints",
    "Team", "PeriodScore", "GameLeader", "Game",
    "PlayerBoxScore", "TeamBoxScore", "PlayAction",
    "StandingsEntry", "PlayerStats", "TeamStats",
    "parse_game_date", "next_day", "prev_day", "game_date_to_season",
]
```

- [ ] **Step 2: Write a live integration test (marked to skip in CI)**

Create `tests/test_integration.py`:
```python
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
    # May be empty on off-days, but should not error
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
```

- [ ] **Step 3: Create pytest config to exclude integration tests by default**

Create `pytest.ini`:
```ini
[pytest]
markers =
    integration: live API tests (deselect with '-m "not integration"')
addopts = -m "not integration"
```

- [ ] **Step 4: Run unit tests (should skip integration)**

```bash
pytest tests/ -v
```
Expected: all unit tests pass, integration tests skipped

- [ ] **Step 5: Run integration tests against real API**

```bash
pytest tests/test_integration.py -v -m integration
```
Expected: all 7 pass (requires internet)

- [ ] **Step 6: Commit**

```bash
git add nba_api/__init__.py tests/test_integration.py pytest.ini
git commit -m "feat: add package exports and live integration tests"
```

---

## Summary

After completing all 8 tasks, the `nba_api` package provides:

- **10 data models** covering games, box scores, play-by-play, standings, player stats, and team stats
- **Endpoint construction** for all 7 NBA API endpoints (CDN + stats.nba.com)
- **Date utilities** for parsing, navigation, and season calculation
- **API client** with JSON→model parsing for all endpoints, in-memory caching, and a requests session with proper headers
- **Full test suite** with fixture-based unit tests and optional live integration tests

The CLI (Plan 2) and GUI (Plan 3) will import `from nba_api import NBAClient` and use the public methods:
- `client.get_scoreboard(date)` → `list[Game]`
- `client.get_boxscore(game_id)` → `tuple[TeamBoxScore, TeamBoxScore]`
- `client.get_playbyplay(game_id)` → `list[PlayAction]`
- `client.get_standings(season)` → `list[StandingsEntry]`
- `client.get_player_stats(season)` → `list[PlayerStats]`
- `client.get_team_stats(season)` → `list[TeamStats]`
