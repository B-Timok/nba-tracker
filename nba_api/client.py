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
