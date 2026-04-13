export interface Team {
	team_id: number;
	name: string;
	city: string;
	tricode: string;
	wins: number;
	losses: number;
	score: number;
	record: string;
	periods: { period: number; score: number }[];
}

export interface GameLeader {
	name: string;
	points: number;
	rebounds: number;
	assists: number;
}

export interface Game {
	game_id: string;
	game_code: string;
	status: number;
	status_text: string;
	period: number;
	game_clock: string;
	game_time_utc: string;
	game_et: string;
	is_scheduled: boolean;
	is_live: boolean;
	is_final: boolean;
	overtime_periods: number;
	home_team: Team;
	away_team: Team;
	home_leader: GameLeader | null;
	away_leader: GameLeader | null;
}

export interface PlayerBox {
	name: string;
	name_short: string;
	jersey_num: string;
	position: string;
	starter: boolean;
	minutes: string;
	points: number;
	rebounds: number;
	assists: number;
	steals: number;
	blocks: number;
	turnovers: number;
	fouls: number;
	fg: string;
	fg_pct: number;
	fg3: string;
	fg3_pct: number;
	ft: string;
	ft_pct: number;
	plus_minus: number;
}

export interface TeamTotals {
	points: number;
	rebounds: number;
	assists: number;
	steals: number;
	blocks: number;
	turnovers: number;
	fouls: number;
	fg: string;
	fg_pct: number;
	fg3: string;
	fg3_pct: number;
	ft: string;
	ft_pct: number;
	points_in_paint: number;
	points_fastbreak: number;
	bench_points: number;
	biggest_lead: number;
}

export interface TeamBoxScore {
	team: Team;
	players: PlayerBox[];
	totals: TeamTotals;
}

export interface BoxScoreResponse {
	home: TeamBoxScore;
	away: TeamBoxScore;
}

export interface PlayAction {
	action_number: number;
	clock: string;
	period: number;
	action_type: string;
	description: string;
	team_tricode: string;
	player_name: string;
	score_home: string;
	score_away: string;
	is_field_goal: boolean;
}

export interface StandingsEntry {
	team_id: number;
	team_name: string;
	team_city: string;
	conference: string;
	division: string;
	playoff_rank: number;
	wins: number;
	losses: number;
	win_pct: number;
	home_record: string;
	road_record: string;
	last_10: string;
	streak: string;
	games_back: number;
	clinch_indicator: string;
	record: string;
}

export interface PlayerStats {
	player_id: number;
	player_name: string;
	team_abbreviation: string;
	age: number;
	gp: number;
	mpg: number;
	ppg: number;
	rpg: number;
	apg: number;
	spg: number;
	bpg: number;
	topg: number;
	fg_pct: number;
	fg3_pct: number;
	ft_pct: number;
	plus_minus: number;
}

export interface TeamStats {
	team_id: number;
	team_name: string;
	gp: number;
	wins: number;
	losses: number;
	win_pct: number;
	ppg: number;
	rpg: number;
	apg: number;
	spg: number;
	bpg: number;
	topg: number;
	fg_pct: number;
	fg3_pct: number;
	ft_pct: number;
	plus_minus: number;
}

export interface PlayerBio {
	player_id: number;
	first_name: string;
	last_name: string;
	display_name: string;
	birthdate: string;
	height: string;
	weight: string;
	position: string;
	jersey: string;
	team_id: number;
	team_name: string;
	team_abbreviation: string;
	team_city: string;
	country: string;
	draft_year: string;
	draft_round: string;
	draft_number: string;
	from_year: string;
	to_year: string;
	roster_status: string;
}

export interface PlayerHeadline {
	pts: number;
	ast: number;
	reb: number;
	pie: number;
	time_frame: string;
}

export interface PlayerSeason {
	season: string;
	team_abbreviation: string;
	gp: number;
	gs: number;
	mpg: number;
	ppg: number;
	rpg: number;
	apg: number;
	spg: number;
	bpg: number;
	topg: number;
	fg_pct: number;
	fg3_pct: number;
	ft_pct: number;
}

export interface PlayerProfile {
	bio: PlayerBio;
	headline: PlayerHeadline;
	seasons: PlayerSeason[];
	career_totals: PlayerSeason;
}

export interface BracketTeam {
	team_id: number;
	city: string;
	name: string;
	tricode: string;
	rank: number;
	wins: number;
	reg_wins: number;
	reg_losses: number;
}

export interface BracketSeries {
	series_id: string;
	round: number;
	series_number: number;
	conference: string;
	round_name: string;
	series_text: string;
	series_status: number;
	series_winner: number;
	high_seed: BracketTeam;
	low_seed: BracketTeam;
	display_order: number;
}

export interface PlayoffBracket {
	season: string;
	current_round: number;
	series: BracketSeries[];
}
