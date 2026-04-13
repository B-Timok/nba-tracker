<script lang="ts">
	import { onMount } from 'svelte';
	import { fly } from 'svelte/transition';
	import { getStandings, getPlayoffs } from '$lib/api';
	import { getTeamColor } from '$lib/teamColors';
	import Skeleton from '$lib/components/Skeleton.svelte';
	import type { StandingsEntry, PlayoffBracket, BracketSeries } from '$lib/types';

	interface ProjectedTeam {
		name: string;
		tricode: string;
		rank: number;
		wins: number;
		losses: number;
		record: string;
	}

	interface ProjectedMatchup {
		high: ProjectedTeam;
		low: ProjectedTeam;
	}

	let loading = true;
	let error = '';
	let mode: 'projected' | 'live' = 'projected';

	// Projected bracket state (from standings)
	let eastMatchups: ProjectedMatchup[] = [];
	let westMatchups: ProjectedMatchup[] = [];
	let eastPlayIn: StandingsEntry[] = [];
	let westPlayIn: StandingsEntry[] = [];

	// Live bracket state (from actual playoff data)
	let bracket: PlayoffBracket | null = null;

	function entryToTeam(e: StandingsEntry): ProjectedTeam {
		return {
			name: e.team_name,
			tricode: e.team_city === 'Oklahoma City' ? 'OKC' :
			         e.team_city === 'Golden State' ? 'GSW' :
			         e.team_city === 'San Antonio' ? 'SAS' :
			         e.team_city === 'New York' ? 'NYK' :
			         e.team_city === 'New Orleans' ? 'NOP' :
			         e.team_city === 'Los Angeles' && e.team_name === 'Lakers' ? 'LAL' :
			         e.team_city === 'Los Angeles' && e.team_name === 'Clippers' ? 'LAC' :
			         e.team_name.substring(0, 3).toUpperCase(),
			rank: e.playoff_rank,
			wins: e.wins,
			losses: e.losses,
			record: e.record,
		};
	}

	function buildProjectedBracket(entries: StandingsEntry[]) {
		for (const conf of ['East', 'West']) {
			const teams = entries
				.filter(e => e.conference === conf)
				.sort((a, b) => a.playoff_rank - b.playoff_rank);

			const top8 = teams.slice(0, 8);
			const playIn = teams.slice(6, 10);

			// 1v8, 2v7, 3v6, 4v5
			const matchups: ProjectedMatchup[] = [
				{ high: entryToTeam(top8[0]), low: entryToTeam(top8[7]) },
				{ high: entryToTeam(top8[1]), low: entryToTeam(top8[6]) },
				{ high: entryToTeam(top8[2]), low: entryToTeam(top8[5]) },
				{ high: entryToTeam(top8[3]), low: entryToTeam(top8[4]) },
			];

			if (conf === 'East') {
				eastMatchups = matchups;
				eastPlayIn = playIn;
			} else {
				westMatchups = matchups;
				westPlayIn = playIn;
			}
		}
	}

	onMount(async () => {
		try {
			// Try actual playoff data for the current season
			try {
				bracket = await getPlayoffs();
				// Only use live mode if bracket is for the current season
				const now = new Date();
				const currentSeasonStart = now.getMonth() >= 8 ? now.getFullYear() : now.getFullYear() - 1;
				const currentSeason = `${currentSeasonStart}-${String(currentSeasonStart + 1).slice(-2)}`;
				const isCurrentSeason = bracket.season === currentSeason;
				const hasActiveSeries = bracket.series.some(s => s.high_seed.team_id > 0);
				if (isCurrentSeason && hasActiveSeries) {
					mode = 'live';
					loading = false;
					return;
				}
			} catch {
				// No live bracket available, fall through to projected
			}

			// Fall back to projected bracket from standings
			mode = 'projected';
			const standings = await getStandings();
			buildProjectedBracket(standings);
		} catch (e: any) {
			error = e.message || 'Failed to load bracket data';
		}
		loading = false;
	});

	// Live bracket helpers
	function getSeriesByRoundConf(round: number, conference: string): BracketSeries[] {
		if (!bracket) return [];
		return bracket.series
			.filter(s => s.round === round && s.conference === conference)
			.sort((a, b) => a.display_order - b.display_order);
	}

	function getFinals(): BracketSeries | null {
		if (!bracket) return null;
		const finals = bracket.series.filter(s => s.round === 4);
		return finals.length > 0 ? finals[0] : null;
	}

	function isWinner(series: BracketSeries, seed: 'high' | 'low'): boolean {
		if (!series.series_winner) return false;
		const team = seed === 'high' ? series.high_seed : series.low_seed;
		return series.series_winner === team.team_id;
	}

	function isLoser(series: BracketSeries, seed: 'high' | 'low'): boolean {
		if (!series.series_winner) return false;
		return !isWinner(series, seed);
	}

	function hasTeams(series: BracketSeries): boolean {
		return series.high_seed.team_id > 0 && series.low_seed.team_id > 0;
	}

	$: finals = getFinals();
</script>

<div class="playoffs-page">
	{#if loading}
		<h1>Playoffs</h1>
		<Skeleton width="100%" height="600px" />
	{:else if error}
		<h1>Playoffs</h1>
		<div class="error">{error}</div>
	{:else if mode === 'projected'}
		<!-- PROJECTED BRACKET FROM STANDINGS -->
		<h1>Projected Playoff Bracket</h1>
		<p class="subtitle">Based on current standings. Updates as the season progresses.</p>

		<div class="projected-container">
			<!-- East bracket -->
			<div class="projected-conf">
				<div class="conf-label">Eastern Conference</div>
				<div class="projected-matchups">
					{#each eastMatchups as matchup, i}
						<div class="matchup" in:fly={{ x: -20, duration: 300, delay: i * 100 }}>
							<div class="team-row" style="--team-color: {getTeamColor(matchup.high.tricode)}">
								<span class="seed">{matchup.high.rank}</span>
								<span class="team-name">{matchup.high.name}</span>
								<span class="team-record">{matchup.high.record}</span>
							</div>
							<div class="vs-divider">vs</div>
							<div class="team-row" style="--team-color: {getTeamColor(matchup.low.tricode)}">
								<span class="seed">{matchup.low.rank}</span>
								<span class="team-name">{matchup.low.name}</span>
								<span class="team-record">{matchup.low.record}</span>
							</div>
						</div>
					{/each}
				</div>

				{#if eastPlayIn.length > 0}
					<div class="playin-section">
						<div class="playin-label">Play-In Tournament</div>
						{#each eastPlayIn as team, i}
							<div class="playin-team" in:fly={{ x: -10, duration: 200, delay: i * 50 + 400 }}>
								<span class="seed">{team.playoff_rank}</span>
								<span class="team-name">{team.team_name}</span>
								<span class="team-record">{team.record}</span>
							</div>
						{/each}
					</div>
				{/if}
			</div>

			<!-- West bracket -->
			<div class="projected-conf">
				<div class="conf-label">Western Conference</div>
				<div class="projected-matchups">
					{#each westMatchups as matchup, i}
						<div class="matchup" in:fly={{ x: 20, duration: 300, delay: i * 100 }}>
							<div class="team-row" style="--team-color: {getTeamColor(matchup.high.tricode)}">
								<span class="seed">{matchup.high.rank}</span>
								<span class="team-name">{matchup.high.name}</span>
								<span class="team-record">{matchup.high.record}</span>
							</div>
							<div class="vs-divider">vs</div>
							<div class="team-row" style="--team-color: {getTeamColor(matchup.low.tricode)}">
								<span class="seed">{matchup.low.rank}</span>
								<span class="team-name">{matchup.low.name}</span>
								<span class="team-record">{matchup.low.record}</span>
							</div>
						</div>
					{/each}
				</div>

				{#if westPlayIn.length > 0}
					<div class="playin-section">
						<div class="playin-label">Play-In Tournament</div>
						{#each westPlayIn as team, i}
							<div class="playin-team" in:fly={{ x: 10, duration: 200, delay: i * 50 + 400 }}>
								<span class="seed">{team.playoff_rank}</span>
								<span class="team-name">{team.team_name}</span>
								<span class="team-record">{team.record}</span>
							</div>
						{/each}
					</div>
				{/if}
			</div>
		</div>

	{:else if bracket}
		<!-- LIVE BRACKET -->
		<h1>Playoffs {bracket.season}</h1>

		<div class="bracket-container">
			<div class="conf-label east-label">Eastern Conference</div>
			<div class="placeholder"></div>
			<div class="conf-label west-label">Western Conference</div>

			{#each [1, 2, 3] as round}
				<div class="round round-{round} east-round">
					{#each getSeriesByRoundConf(round, 'East') as series, i}
						<div class="matchup" in:fly={{ x: -20, duration: 300, delay: i * 100 + round * 150 }}>
							{#if hasTeams(series)}
								<div class="team-row" class:winner={isWinner(series, 'high')} class:loser={isLoser(series, 'high')} style="--team-color: {getTeamColor(series.high_seed.tricode)}">
									<span class="seed">{series.high_seed.rank}</span>
									<span class="team-name">{series.high_seed.name}</span>
									<span class="series-wins">{series.high_seed.wins}</span>
								</div>
								<div class="team-row" class:winner={isWinner(series, 'low')} class:loser={isLoser(series, 'low')} style="--team-color: {getTeamColor(series.low_seed.tricode)}">
									<span class="seed">{series.low_seed.rank}</span>
									<span class="team-name">{series.low_seed.name}</span>
									<span class="series-wins">{series.low_seed.wins}</span>
								</div>
								<div class="series-status">{series.series_text}</div>
							{:else}
								<div class="team-row tbd"><span class="team-name">TBD</span></div>
								<div class="team-row tbd"><span class="team-name">TBD</span></div>
							{/if}
						</div>
					{/each}
				</div>
			{/each}

			<div class="finals">
				<div class="finals-label">NBA Finals</div>
				{#if finals && hasTeams(finals)}
					<div class="matchup finals-matchup" in:fly={{ y: -20, duration: 400, delay: 600 }}>
						<div class="team-row" class:winner={isWinner(finals, 'high')} class:loser={isLoser(finals, 'high')} style="--team-color: {getTeamColor(finals.high_seed.tricode)}">
							<span class="seed">{finals.high_seed.rank}</span>
							<span class="team-name">{finals.high_seed.name}</span>
							<span class="series-wins">{finals.high_seed.wins}</span>
						</div>
						<div class="team-row" class:winner={isWinner(finals, 'low')} class:loser={isLoser(finals, 'low')} style="--team-color: {getTeamColor(finals.low_seed.tricode)}">
							<span class="seed">{finals.low_seed.rank}</span>
							<span class="team-name">{finals.low_seed.name}</span>
							<span class="series-wins">{finals.low_seed.wins}</span>
						</div>
						<div class="series-status">{finals.series_text}</div>
					</div>
				{:else}
					<div class="matchup finals-matchup">
						<div class="team-row tbd"><span class="team-name">East Champion</span></div>
						<div class="team-row tbd"><span class="team-name">West Champion</span></div>
					</div>
				{/if}
			</div>

			{#each [3, 2, 1] as round}
				<div class="round round-{round} west-round">
					{#each getSeriesByRoundConf(round, 'West') as series, i}
						<div class="matchup" in:fly={{ x: 20, duration: 300, delay: i * 100 + (4 - round) * 150 }}>
							{#if hasTeams(series)}
								<div class="team-row" class:winner={isWinner(series, 'high')} class:loser={isLoser(series, 'high')} style="--team-color: {getTeamColor(series.high_seed.tricode)}">
									<span class="series-wins">{series.high_seed.wins}</span>
									<span class="team-name right">{series.high_seed.name}</span>
									<span class="seed">{series.high_seed.rank}</span>
								</div>
								<div class="team-row" class:winner={isWinner(series, 'low')} class:loser={isLoser(series, 'low')} style="--team-color: {getTeamColor(series.low_seed.tricode)}">
									<span class="series-wins">{series.low_seed.wins}</span>
									<span class="team-name right">{series.low_seed.name}</span>
									<span class="seed">{series.low_seed.rank}</span>
								</div>
								<div class="series-status">{series.series_text}</div>
							{:else}
								<div class="team-row tbd"><span class="team-name">TBD</span></div>
								<div class="team-row tbd"><span class="team-name">TBD</span></div>
							{/if}
						</div>
					{/each}
				</div>
			{/each}
		</div>
	{/if}
</div>

<style>
	.playoffs-page {
		max-width: 1400px;
		margin: 0 auto;
	}

	h1 {
		font-size: 2rem;
		margin-bottom: 0.5rem;
		text-align: center;
		background: linear-gradient(135deg, var(--text-primary), var(--accent-orange));
		-webkit-background-clip: text;
		-webkit-text-fill-color: transparent;
		background-clip: text;
	}

	.subtitle {
		text-align: center;
		color: var(--text-muted);
		font-size: 0.9rem;
		margin-bottom: 2rem;
	}

	/* ===== PROJECTED BRACKET ===== */

	.projected-container {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 2rem;
	}

	.projected-conf {
		display: flex;
		flex-direction: column;
		gap: 1rem;
	}

	.projected-matchups {
		display: flex;
		flex-direction: column;
		gap: 0.75rem;
	}

	.vs-divider {
		text-align: center;
		font-size: 0.65rem;
		font-weight: 700;
		text-transform: uppercase;
		letter-spacing: 0.1em;
		color: var(--text-muted);
		padding: 0.15rem 0;
		border-top: 1px solid var(--border-subtle);
	}

	.team-record {
		font-size: 0.75rem;
		color: var(--text-muted);
		font-variant-numeric: tabular-nums;
	}

	.playin-section {
		margin-top: 0.5rem;
		padding-top: 1rem;
		border-top: 1px dashed var(--border-subtle);
	}

	.playin-label {
		font-family: var(--font-heading);
		font-size: 0.75rem;
		font-weight: 700;
		text-transform: uppercase;
		letter-spacing: 0.1em;
		color: var(--text-muted);
		margin-bottom: 0.5rem;
	}

	.playin-team {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.4rem 0.75rem;
		font-size: 0.85rem;
	}

	.playin-team .team-name {
		flex: 1;
	}

	/* ===== LIVE BRACKET ===== */

	.bracket-container {
		display: grid;
		grid-template-columns: 1fr 1fr 1fr auto 1fr 1fr 1fr;
		grid-template-rows: auto 1fr;
		gap: 0.5rem;
		align-items: start;
	}

	.east-label { grid-column: 1 / 4; grid-row: 1; }
	.placeholder { grid-column: 4; grid-row: 1; }
	.west-label { grid-column: 5 / 8; grid-row: 1; }

	.round {
		display: flex;
		flex-direction: column;
		justify-content: space-around;
		min-height: 520px;
		gap: 0.5rem;
		grid-row: 2;
	}

	.east-round.round-1 { grid-column: 1; }
	.east-round.round-2 { grid-column: 2; }
	.east-round.round-3 { grid-column: 3; }

	.finals {
		grid-column: 4;
		grid-row: 2;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		min-height: 520px;
		gap: 1rem;
		padding: 0 0.5rem;
	}

	.west-round.round-3 { grid-column: 5; }
	.west-round.round-2 { grid-column: 6; }
	.west-round.round-1 { grid-column: 7; }

	.finals-label {
		font-family: var(--font-heading);
		font-size: 1rem;
		font-weight: 700;
		color: var(--accent-orange);
		text-transform: uppercase;
		letter-spacing: 0.1em;
	}

	.finals-matchup {
		min-width: 180px;
	}

	.finals-matchup .team-name {
		font-size: 0.9rem;
	}

	.finals-matchup .series-wins {
		font-size: 1.2rem;
	}

	/* ===== SHARED ===== */

	.conf-label {
		font-family: var(--font-heading);
		font-size: 0.85rem;
		font-weight: 700;
		color: var(--text-secondary);
		text-transform: uppercase;
		letter-spacing: 0.1em;
		text-align: center;
		padding-bottom: 0.5rem;
	}

	.matchup {
		background: var(--bg-card);
		border: 1px solid var(--border-subtle);
		border-radius: var(--radius-sm);
		overflow: hidden;
	}

	.team-row {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		padding: 0.5rem 0.75rem;
		border-left: 3px solid var(--team-color, var(--border-subtle));
		transition: all 0.2s ease;
	}

	.west-round .team-row {
		border-left: none;
		border-right: 3px solid var(--team-color, var(--border-subtle));
	}

	.team-row + .team-row {
		border-top: 1px solid var(--border-subtle);
	}

	.team-row.winner {
		background: rgba(255, 255, 255, 0.05);
	}

	.team-row.winner .team-name {
		color: #ffffff;
		font-weight: 700;
	}

	.team-row.winner .series-wins {
		color: var(--accent-green);
		font-weight: 700;
	}

	.team-row.loser {
		opacity: 0.4;
	}

	.team-row.tbd {
		border-left-color: var(--border-subtle);
		border-right-color: var(--border-subtle);
	}

	.seed {
		font-size: 0.7rem;
		font-weight: 700;
		color: var(--text-muted);
		min-width: 1rem;
		text-align: center;
	}

	.team-name {
		font-family: var(--font-heading);
		font-size: 0.8rem;
		font-weight: 600;
		flex: 1;
		white-space: nowrap;
	}

	.team-name.right {
		text-align: right;
	}

	.tbd .team-name {
		color: var(--text-muted);
		font-style: italic;
	}

	.series-wins {
		font-family: var(--font-heading);
		font-size: 1rem;
		font-weight: 700;
		min-width: 1.2rem;
		text-align: center;
	}

	.series-status {
		font-size: 0.65rem;
		color: var(--text-muted);
		text-align: center;
		padding: 0.3rem 0.5rem;
		border-top: 1px solid var(--border-subtle);
		background: rgba(0, 0, 0, 0.2);
	}

	.error {
		text-align: center;
		padding: 3rem;
		color: var(--accent-red);
	}
</style>
