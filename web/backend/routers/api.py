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
    games = client.get_scoreboard(d)
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
    entries = client.get_standings(season)
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
    stats = client.get_player_stats(season)
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
    stats = client.get_team_stats(season)
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
