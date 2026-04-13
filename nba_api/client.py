import requests
import time
from datetime import date
from typing import Optional
from nba_api.endpoints import NBAEndpoints
from nba_api.models import (
    Team, PeriodScore, GameLeader, Game,
    PlayerBoxScore, TeamBoxScore, PlayAction,
    StandingsEntry, PlayerStats, TeamStats,
)
from nba_api.date_utils import game_date_to_season

REQUEST_TIMEOUT = 9

CACHE_LONG = 3600  # 1 hour for completed data
CACHE_NONE = 0     # No caching for live data


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


class NBAClient:
    def __init__(self):
        self._session = requests.Session()
        self._session.headers.update(NBAEndpoints.stats_headers())
        self._cache = _Cache()

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
                team_tricode=col(row, "TeamSlug"),
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

        # Only cache if no live games
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
