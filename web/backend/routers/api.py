from datetime import date
from dataclasses import asdict
from fastapi import APIRouter, HTTPException, Query

from nba_api import NBAClient, parse_game_date, game_date_to_season

router = APIRouter(prefix="/api")
client = NBAClient()


def _team_dict(team) -> dict:
    return {
        "team_id": team.team_id,
        "name": team.name,
        "city": team.city,
        "tricode": team.tricode,
        "wins": team.wins,
        "losses": team.losses,
        "score": team.score,
        "record": team.record,
        "periods": [{"period": p.period, "score": p.score} for p in team.periods],
    }


def _leader_dict(leader) -> dict | None:
    if not leader:
        return None
    return {
        "name": leader.name,
        "points": leader.points,
        "rebounds": leader.rebounds,
        "assists": leader.assists,
    }


def _game_dict(game) -> dict:
    return {
        "game_id": game.game_id,
        "game_code": game.game_code,
        "status": game.status,
        "status_text": game.status_text,
        "period": game.period,
        "game_clock": game.game_clock,
        "game_time_utc": game.game_time_utc,
        "game_et": game.game_et,
        "is_scheduled": game.is_scheduled,
        "is_live": game.is_live,
        "is_final": game.is_final,
        "overtime_periods": game.overtime_periods,
        "home_team": _team_dict(game.home_team),
        "away_team": _team_dict(game.away_team),
        "home_leader": _leader_dict(game.home_leader),
        "away_leader": _leader_dict(game.away_leader),
    }


def _player_box_dict(player) -> dict:
    return {
        "name": player.name,
        "name_short": player.name_short,
        "jersey_num": player.jersey_num,
        "position": player.position,
        "starter": player.starter,
        "minutes": player.minutes_display,
        "points": player.points,
        "rebounds": player.rebounds,
        "assists": player.assists,
        "steals": player.steals,
        "blocks": player.blocks,
        "turnovers": player.turnovers,
        "fouls": player.fouls,
        "fg": f"{player.fg_made}-{player.fg_attempted}",
        "fg_pct": player.fg_pct,
        "fg3": f"{player.fg3_made}-{player.fg3_attempted}",
        "fg3_pct": player.fg3_pct,
        "ft": f"{player.ft_made}-{player.ft_attempted}",
        "ft_pct": player.ft_pct,
        "plus_minus": player.plus_minus,
    }


def _team_box_dict(box) -> dict:
    return {
        "team": _team_dict(box.team),
        "players": [_player_box_dict(p) for p in box.players],
        "totals": {
            "points": box.total_points,
            "rebounds": box.total_rebounds,
            "assists": box.total_assists,
            "steals": box.total_steals,
            "blocks": box.total_blocks,
            "turnovers": box.total_turnovers,
            "fouls": box.total_fouls,
            "fg": f"{box.fg_made}-{box.fg_attempted}",
            "fg_pct": box.fg_pct,
            "fg3": f"{box.fg3_made}-{box.fg3_attempted}",
            "fg3_pct": box.fg3_pct,
            "ft": f"{box.ft_made}-{box.ft_attempted}",
            "ft_pct": box.ft_pct,
            "points_in_paint": box.points_in_paint,
            "points_fastbreak": box.points_fastbreak,
            "bench_points": box.bench_points,
            "biggest_lead": box.biggest_lead,
        },
    }


@router.get("/scoreboard/{date_str}")
def get_scoreboard(date_str: str):
    d = parse_game_date(date_str)
    if d is None:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")
    try:
        games = client.get_scoreboard_cdn(d)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load scoreboard: {e}")
    return [_game_dict(g) for g in games]


@router.get("/game/{game_id}/boxscore")
def get_boxscore(game_id: str):
    try:
        home_box, away_box = client.get_boxscore(game_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Box score not found: {e}")
    return {"home": _team_box_dict(home_box), "away": _team_box_dict(away_box)}


@router.get("/game/{game_id}/playbyplay")
def get_playbyplay(game_id: str):
    try:
        actions = client.get_playbyplay(game_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Play-by-play not found: {e}")
    return [
        {
            "action_number": a.action_number,
            "clock": a.clock,
            "period": a.period,
            "action_type": a.action_type,
            "description": a.description,
            "team_tricode": a.team_tricode,
            "player_name": a.player_name,
            "score_home": a.score_home,
            "score_away": a.score_away,
            "is_field_goal": a.is_field_goal,
        }
        for a in actions
    ]


@router.get("/standings")
def get_standings(season: str = Query(default=None)):
    if not season:
        season = game_date_to_season(date.today())
    try:
        entries = client.get_standings(season)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load standings: {e}")
    return [
        {
            "team_id": e.team_id,
            "team_name": e.team_name,
            "team_city": e.team_city,
            "conference": e.conference,
            "division": e.division,
            "playoff_rank": e.playoff_rank,
            "wins": e.wins,
            "losses": e.losses,
            "win_pct": e.win_pct,
            "home_record": e.home_record,
            "road_record": e.road_record,
            "last_10": e.last_10,
            "streak": e.streak,
            "games_back": e.games_back,
            "clinch_indicator": e.clinch_indicator,
            "record": e.record,
        }
        for e in entries
    ]


@router.get("/stats/players")
def get_player_stats(season: str = Query(default=None)):
    if not season:
        season = game_date_to_season(date.today())
    try:
        stats = client.get_player_stats(season)
    except Exception as e:
        raise HTTPException(status_code=503, detail="Player stats temporarily unavailable")
    return [
        {
            "player_id": s.player_id,
            "player_name": s.player_name,
            "team_abbreviation": s.team_abbreviation,
            "age": s.age,
            "gp": s.gp,
            "mpg": s.mpg,
            "ppg": s.ppg,
            "rpg": s.rpg,
            "apg": s.apg,
            "spg": s.spg,
            "bpg": s.bpg,
            "topg": s.topg,
            "fg_pct": s.fg_pct,
            "fg3_pct": s.fg3_pct,
            "ft_pct": s.ft_pct,
            "plus_minus": s.plus_minus,
        }
        for s in stats
    ]


@router.get("/stats/teams")
def get_team_stats(season: str = Query(default=None)):
    if not season:
        season = game_date_to_season(date.today())
    try:
        stats = client.get_team_stats(season)
    except Exception as e:
        raise HTTPException(status_code=503, detail="Team stats temporarily unavailable")
    return [
        {
            "team_id": s.team_id,
            "team_name": s.team_name,
            "gp": s.gp,
            "wins": s.wins,
            "losses": s.losses,
            "win_pct": s.win_pct,
            "ppg": s.ppg,
            "rpg": s.rpg,
            "apg": s.apg,
            "spg": s.spg,
            "bpg": s.bpg,
            "topg": s.topg,
            "fg_pct": s.fg_pct,
            "fg3_pct": s.fg3_pct,
            "ft_pct": s.ft_pct,
            "plus_minus": s.plus_minus,
        }
        for s in stats
    ]


@router.get("/player/{player_id}")
def get_player_profile(player_id: int):
    # Fetch player info
    try:
        info_resp = client._session.get(
            f"https://stats.nba.com/stats/commonplayerinfo?PlayerID={player_id}",
            timeout=5,
        )
        info_resp.raise_for_status()
        info_data = info_resp.json()
    except Exception as e:
        raise HTTPException(status_code=503, detail="Player profile temporarily unavailable")

    # Fetch career stats
    try:
        career_resp = client._session.get(
            f"https://stats.nba.com/stats/playercareerstats?PlayerID={player_id}&PerMode=PerGame",
            timeout=5,
        )
        career_resp.raise_for_status()
        career_data = career_resp.json()
    except Exception as e:
        raise HTTPException(status_code=503, detail="Player career stats temporarily unavailable")

    # Parse player info
    info_sets = info_data.get("resultSets", [])
    bio = {}
    headline = {}

    for rs in info_sets:
        name = rs.get("name", "")
        headers_list = rs.get("headers", [])
        rows = rs.get("rowSet", [])
        if name == "CommonPlayerInfo" and rows:
            row = rows[0]
            def col(n):
                try: return row[headers_list.index(n)]
                except: return None
            bio = {
                "player_id": col("PERSON_ID"),
                "first_name": col("FIRST_NAME"),
                "last_name": col("LAST_NAME"),
                "display_name": col("DISPLAY_FIRST_LAST"),
                "birthdate": col("BIRTHDATE"),
                "height": col("HEIGHT"),
                "weight": col("WEIGHT"),
                "position": col("POSITION"),
                "jersey": col("JERSEY"),
                "team_id": col("TEAM_ID"),
                "team_name": col("TEAM_NAME"),
                "team_abbreviation": col("TEAM_ABBREVIATION"),
                "team_city": col("TEAM_CITY"),
                "country": col("COUNTRY"),
                "draft_year": col("DRAFT_YEAR"),
                "draft_round": col("DRAFT_ROUND"),
                "draft_number": col("DRAFT_NUMBER"),
                "from_year": col("FROM_YEAR"),
                "to_year": col("TO_YEAR"),
                "roster_status": col("ROSTERSTATUS"),
            }
        elif name == "PlayerHeadlineStats" and rows:
            row = rows[0]
            def col2(n):
                try: return row[headers_list.index(n)]
                except: return None
            headline = {
                "pts": col2("PTS"),
                "ast": col2("AST"),
                "reb": col2("REB"),
                "pie": col2("PIE"),
                "time_frame": col2("TimeFrame"),
            }

    # Parse career stats
    career_sets = career_data.get("resultSets", [])
    seasons = []
    career_totals = {}

    for rs in career_sets:
        name = rs.get("name", "")
        headers_list = rs.get("headers", [])
        rows = rs.get("rowSet", [])

        if name == "SeasonTotalsRegularSeason":
            for row in rows:
                def scol(n):
                    try: return row[headers_list.index(n)]
                    except: return None
                seasons.append({
                    "season": scol("SEASON_ID"),
                    "team_abbreviation": scol("TEAM_ABBREVIATION"),
                    "gp": scol("GP"),
                    "gs": scol("GS"),
                    "mpg": scol("MIN"),
                    "ppg": scol("PTS"),
                    "rpg": scol("REB"),
                    "apg": scol("AST"),
                    "spg": scol("STL"),
                    "bpg": scol("BLK"),
                    "topg": scol("TOV"),
                    "fg_pct": scol("FG_PCT"),
                    "fg3_pct": scol("FG3_PCT"),
                    "ft_pct": scol("FT_PCT"),
                })
        elif name == "CareerTotalsRegularSeason" and rows:
            row = rows[0]
            def ccol(n):
                try: return row[headers_list.index(n)]
                except: return None
            career_totals = {
                "gp": ccol("GP"),
                "gs": ccol("GS"),
                "mpg": ccol("MIN"),
                "ppg": ccol("PTS"),
                "rpg": ccol("REB"),
                "apg": ccol("AST"),
                "spg": ccol("STL"),
                "bpg": ccol("BLK"),
                "topg": ccol("TOV"),
                "fg_pct": ccol("FG_PCT"),
                "fg3_pct": ccol("FG3_PCT"),
                "ft_pct": ccol("FT_PCT"),
            }

    return {
        "bio": bio,
        "headline": headline,
        "seasons": seasons,
        "career_totals": career_totals,
    }


@router.get("/playin")
def get_playin():
    """Return play-in tournament games from the cached schedule.

    Play-in game IDs are prefixed '005' (vs '002' regular season, '004' playoffs).
    The client is responsible for mapping tricodes to conferences via standings.
    """
    try:
        schedule = client.get_schedule()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Schedule unavailable: {e}")

    games = []
    for gd in schedule.get("leagueSchedule", {}).get("gameDates", []):
        for g in gd.get("games", []):
            gid = g.get("gameId", "")
            if not gid.startswith("005"):
                continue
            home = g.get("homeTeam", {})
            away = g.get("awayTeam", {})
            games.append({
                "game_id": gid,
                "date": gd.get("gameDate", "").split()[0],
                "status": g.get("gameStatus", 1),
                "status_text": g.get("gameStatusText", ""),
                "home_tricode": home.get("teamTricode", ""),
                "home_score": home.get("score", 0),
                "away_tricode": away.get("teamTricode", ""),
                "away_score": away.get("score", 0),
            })
    return games


@router.get("/playoffs")
def get_playoffs(season: str = Query(default=None)):
    if not season:
        season = game_date_to_season(date.today())

    # Season is like "2024-25", we need the end year "2025"
    end_year = season.split("-")[0]  # "2024"
    end_year = str(int(end_year) + 1)  # "2025"

    # Try requested season first, then fall back to previous years
    data = None
    actual_year = int(end_year)
    for year in range(actual_year, actual_year - 3, -1):
        url = f"https://cdn.nba.com/static/json/staticData/brackets/{year}/PlayoffBracket.json"
        try:
            resp = client._session.get(url, timeout=5)
            resp.raise_for_status()
            data = resp.json()
            season = f"{year - 1}-{str(year)[-2:]}"
            break
        except Exception:
            continue

    if not data:
        raise HTTPException(status_code=404, detail="No playoff bracket data available")

    bracket = data.get("bracket", {})
    series_list = bracket.get("playoffBracketSeries", [])

    return {
        "season": season,
        "current_round": bracket.get("currentRound", 0),
        "series": [
            {
                "series_id": s.get("seriesId", ""),
                "round": s.get("roundNumber", 0),
                "series_number": s.get("seriesNumber", 0),
                "conference": s.get("seriesConference", ""),
                "round_name": s.get("poRoundDesc", ""),
                "series_text": s.get("seriesText", ""),
                "series_status": s.get("seriesStatus", 0),
                "series_winner": s.get("seriesWinner", 0),
                "high_seed": {
                    "team_id": s.get("highSeedId", 0),
                    "city": s.get("highSeedCity", ""),
                    "name": s.get("highSeedName", ""),
                    "tricode": s.get("highSeedTricode", ""),
                    "rank": s.get("highSeedRank", 0),
                    "wins": s.get("highSeedSeriesWins", 0),
                    "reg_wins": s.get("highSeedRegSeasonWins", 0),
                    "reg_losses": s.get("highSeedRegSeasonLosses", 0),
                },
                "low_seed": {
                    "team_id": s.get("lowSeedId", 0),
                    "city": s.get("lowSeedCity", ""),
                    "name": s.get("lowSeedName", ""),
                    "tricode": s.get("lowSeedTricode", ""),
                    "rank": s.get("lowSeedRank", 0),
                    "wins": s.get("lowSeedSeriesWins", 0),
                    "reg_wins": s.get("lowSeedRegSeasonWins", 0),
                    "reg_losses": s.get("lowSeedRegSeasonLosses", 0),
                },
                "display_order": s.get("displayOrderNumber", 0),
            }
            for s in series_list
        ],
    }
