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
