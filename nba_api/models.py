from dataclasses import dataclass, field
from typing import Optional
import re


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
