import type {
	Game, BoxScoreResponse, PlayAction,
	StandingsEntry, PlayerStats, TeamStats
} from '$lib/types';

const BASE = '/api';

async function fetchJSON<T>(url: string): Promise<T> {
	const resp = await fetch(url);
	if (!resp.ok) {
		const err = await resp.json().catch(() => ({ detail: resp.statusText }));
		throw new Error(err.detail || 'API error');
	}
	return resp.json();
}

export async function getScoreboard(date: string): Promise<Game[]> {
	return fetchJSON<Game[]>(`${BASE}/scoreboard/${date}`);
}

export async function getBoxScore(gameId: string): Promise<BoxScoreResponse> {
	return fetchJSON<BoxScoreResponse>(`${BASE}/game/${gameId}/boxscore`);
}

export async function getPlayByPlay(gameId: string): Promise<PlayAction[]> {
	return fetchJSON<PlayAction[]>(`${BASE}/game/${gameId}/playbyplay`);
}

export async function getStandings(season?: string): Promise<StandingsEntry[]> {
	const params = season ? `?season=${season}` : '';
	return fetchJSON<StandingsEntry[]>(`${BASE}/standings${params}`);
}

export async function getPlayerStats(season?: string): Promise<PlayerStats[]> {
	const params = season ? `?season=${season}` : '';
	return fetchJSON<PlayerStats[]>(`${BASE}/stats/players${params}`);
}

export async function getTeamStats(season?: string): Promise<TeamStats[]> {
	const params = season ? `?season=${season}` : '';
	return fetchJSON<TeamStats[]>(`${BASE}/stats/teams${params}`);
}
