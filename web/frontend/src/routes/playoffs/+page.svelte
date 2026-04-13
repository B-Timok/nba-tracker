<script lang="ts">
	import { onMount } from 'svelte';
	import { fly } from 'svelte/transition';
	import { getStandings, getPlayoffs } from '$lib/api';
	import { getTeamColor } from '$lib/teamColors';
	import Skeleton from '$lib/components/Skeleton.svelte';
	import type { StandingsEntry, PlayoffBracket, BracketSeries, BracketTeam } from '$lib/types';

	let loading = true;
	let error = '';
	let isProjected = false;
	let seasonLabel = '';

	// Bracket data — same format for both projected and live
	let allSeries: BracketSeries[] = [];

	// Play-in teams (projected mode only)
	let eastPlayIn: StandingsEntry[] = [];
	let westPlayIn: StandingsEntry[] = [];

	function entryToBracketTeam(e: StandingsEntry): BracketTeam {
		// Derive tricode from city/name
		const tricodeMap: Record<string, string> = {
			'Oklahoma City Thunder': 'OKC', 'Golden State Warriors': 'GSW',
			'San Antonio Spurs': 'SAS', 'New York Knicks': 'NYK',
			'New Orleans Pelicans': 'NOP', 'Los Angeles Lakers': 'LAL',
			'Los Angeles Clippers': 'LAC', 'Portland Trail Blazers': 'POR',
		};
		const key = `${e.team_city} ${e.team_name}`;
		const tricode = tricodeMap[key] || e.team_name.substring(0, 3).toUpperCase();

		return {
			team_id: e.team_id,
			city: e.team_city,
			name: e.team_name,
			tricode,
			rank: e.playoff_rank,
			wins: 0,
			reg_wins: e.wins,
			reg_losses: e.losses,
		};
	}

	function buildProjectedBracket(entries: StandingsEntry[]) {
		const series: BracketSeries[] = [];
		let orderCounter = 1;

		for (const conf of ['East', 'West'] as const) {
			const teams = entries
				.filter(e => e.conference === conf)
				.sort((a, b) => a.playoff_rank - b.playoff_rank);

			const top8 = teams.slice(0, 8);

			// Round 1: 1v8, 2v7, 3v6, 4v5
			const pairings = [[0, 7], [1, 6], [2, 5], [3, 4]];
			for (const [hi, lo] of pairings) {
				series.push({
					series_id: `proj-${conf}-r1-${orderCounter}`,
					round: 1,
					series_number: orderCounter,
					conference: conf,
					round_name: 'First Round',
					series_text: `(${top8[hi].wins}-${top8[hi].losses}) vs (${top8[lo].wins}-${top8[lo].losses})`,
					series_status: 0,
					series_winner: 0,
					high_seed: entryToBracketTeam(top8[hi]),
					low_seed: entryToBracketTeam(top8[lo]),
					display_order: orderCounter,
				});
				orderCounter++;
			}

			// Round 2: TBD placeholders (winners of R1)
			for (let i = 0; i < 2; i++) {
				series.push({
					series_id: `proj-${conf}-r2-${orderCounter}`,
					round: 2,
					series_number: orderCounter,
					conference: conf,
					round_name: 'Conf. Semis',
					series_text: '',
					series_status: 0,
					series_winner: 0,
					high_seed: { team_id: 0, city: '', name: '', tricode: '', rank: 0, wins: 0, reg_wins: 0, reg_losses: 0 },
					low_seed: { team_id: 0, city: '', name: '', tricode: '', rank: 0, wins: 0, reg_wins: 0, reg_losses: 0 },
					display_order: orderCounter,
				});
				orderCounter++;
			}

			// Round 3: TBD (Conf Finals)
			series.push({
				series_id: `proj-${conf}-r3-${orderCounter}`,
				round: 3,
				series_number: orderCounter,
				conference: conf,
				round_name: 'Conf. Finals',
				series_text: '',
				series_status: 0,
				series_winner: 0,
				high_seed: { team_id: 0, city: '', name: '', tricode: '', rank: 0, wins: 0, reg_wins: 0, reg_losses: 0 },
				low_seed: { team_id: 0, city: '', name: '', tricode: '', rank: 0, wins: 0, reg_wins: 0, reg_losses: 0 },
				display_order: orderCounter,
			});
			orderCounter++;

			// Play-in teams
			const playIn = teams.slice(6, 10);
			if (conf === 'East') eastPlayIn = playIn;
			else westPlayIn = playIn;
		}

		// Finals: TBD
		series.push({
			series_id: 'proj-finals',
			round: 4,
			series_number: orderCounter,
			conference: '',
			round_name: 'NBA Finals',
			series_text: '',
			series_status: 0,
			series_winner: 0,
			high_seed: { team_id: 0, city: '', name: '', tricode: '', rank: 0, wins: 0, reg_wins: 0, reg_losses: 0 },
			low_seed: { team_id: 0, city: '', name: '', tricode: '', rank: 0, wins: 0, reg_wins: 0, reg_losses: 0 },
			display_order: orderCounter,
		});

		allSeries = series;
	}

	onMount(async () => {
		try {
			// Try actual playoff data for the current season
			try {
				const bracket = await getPlayoffs();
				const now = new Date();
				const currentSeasonStart = now.getMonth() >= 8 ? now.getFullYear() : now.getFullYear() - 1;
				const currentSeason = `${currentSeasonStart}-${String(currentSeasonStart + 1).slice(-2)}`;
				const isCurrentSeason = bracket.season === currentSeason;
				const hasActiveSeries = bracket.series.some(s => s.high_seed.team_id > 0);
				if (isCurrentSeason && hasActiveSeries) {
					allSeries = bracket.series;
					seasonLabel = bracket.season;
					isProjected = false;
					loading = false;
					return;
				}
			} catch {
				// Fall through
			}

			// Projected from standings
			isProjected = true;
			const standings = await getStandings();
			buildProjectedBracket(standings);
			const now = new Date();
			const startYear = now.getMonth() >= 8 ? now.getFullYear() : now.getFullYear() - 1;
			seasonLabel = `${startYear}-${String(startYear + 1).slice(-2)}`;
		} catch (e: any) {
			error = e.message || 'Failed to load bracket data';
		}
		loading = false;
	});

	function getSeriesByRoundConf(round: number, conference: string): BracketSeries[] {
		return allSeries
			.filter(s => s.round === round && s.conference === conference)
			.sort((a, b) => a.display_order - b.display_order);
	}

	function getFinals(): BracketSeries | null {
		const finals = allSeries.filter(s => s.round === 4);
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
	{:else}
		<h1>{isProjected ? 'Projected Playoff Bracket' : 'Playoffs'} {seasonLabel}</h1>
		{#if isProjected}
			<p class="subtitle">Based on current standings. Updates as the season progresses.</p>
		{/if}

		<div class="bracket-container">
			<div class="conf-label east-label">Eastern Conference</div>
			<div class="placeholder"></div>
			<div class="conf-label west-label">Western Conference</div>

			<!-- East: R1 → R2 → CF -->
			{#each [1, 2, 3] as round}
				<div class="round round-{round} east-round">
					{#each getSeriesByRoundConf(round, 'East') as series, i}
						<div class="matchup" in:fly={{ x: -20, duration: 300, delay: i * 100 + round * 150 }}>
							{#if hasTeams(series)}
								<div class="team-row" class:winner={isWinner(series, 'high')} class:loser={isLoser(series, 'high')} style="--team-color: {getTeamColor(series.high_seed.tricode)}">
									<span class="seed">{series.high_seed.rank}</span>
									<span class="team-name">{series.high_seed.name}</span>
									{#if isProjected}
										<span class="team-record">{series.high_seed.reg_wins}-{series.high_seed.reg_losses}</span>
									{:else}
										<span class="series-wins">{series.high_seed.wins}</span>
									{/if}
								</div>
								<div class="team-row" class:winner={isWinner(series, 'low')} class:loser={isLoser(series, 'low')} style="--team-color: {getTeamColor(series.low_seed.tricode)}">
									<span class="seed">{series.low_seed.rank}</span>
									<span class="team-name">{series.low_seed.name}</span>
									{#if isProjected}
										<span class="team-record">{series.low_seed.reg_wins}-{series.low_seed.reg_losses}</span>
									{:else}
										<span class="series-wins">{series.low_seed.wins}</span>
									{/if}
								</div>
								{#if series.series_text}
									<div class="series-status">{series.series_text}</div>
								{/if}
							{:else}
								<div class="team-row tbd"><span class="team-name">TBD</span></div>
								<div class="team-row tbd"><span class="team-name">TBD</span></div>
							{/if}
						</div>
					{/each}
				</div>
			{/each}

			<!-- Finals -->
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
						{#if finals.series_text}
							<div class="series-status">{finals.series_text}</div>
						{/if}
					</div>
				{:else}
					<div class="matchup finals-matchup">
						<div class="team-row tbd"><span class="team-name">East Champion</span></div>
						<div class="team-row tbd"><span class="team-name">West Champion</span></div>
					</div>
				{/if}
			</div>

			<!-- West: CF ← R2 ← R1 -->
			{#each [3, 2, 1] as round}
				<div class="round round-{round} west-round">
					{#each getSeriesByRoundConf(round, 'West') as series, i}
						<div class="matchup" in:fly={{ x: 20, duration: 300, delay: i * 100 + (4 - round) * 150 }}>
							{#if hasTeams(series)}
								<div class="team-row" class:winner={isWinner(series, 'high')} class:loser={isLoser(series, 'high')} style="--team-color: {getTeamColor(series.high_seed.tricode)}">
									{#if isProjected}
										<span class="team-record">{series.high_seed.reg_wins}-{series.high_seed.reg_losses}</span>
									{:else}
										<span class="series-wins">{series.high_seed.wins}</span>
									{/if}
									<span class="team-name right">{series.high_seed.name}</span>
									<span class="seed">{series.high_seed.rank}</span>
								</div>
								<div class="team-row" class:winner={isWinner(series, 'low')} class:loser={isLoser(series, 'low')} style="--team-color: {getTeamColor(series.low_seed.tricode)}">
									{#if isProjected}
										<span class="team-record">{series.low_seed.reg_wins}-{series.low_seed.reg_losses}</span>
									{:else}
										<span class="series-wins">{series.low_seed.wins}</span>
									{/if}
									<span class="team-name right">{series.low_seed.name}</span>
									<span class="seed">{series.low_seed.rank}</span>
								</div>
								{#if series.series_text}
									<div class="series-status">{series.series_text}</div>
								{/if}
							{:else}
								<div class="team-row tbd"><span class="team-name">TBD</span></div>
								<div class="team-row tbd"><span class="team-name">TBD</span></div>
							{/if}
						</div>
					{/each}
				</div>
			{/each}
		</div>

		<!-- Play-In section (projected mode only) -->
		{#if isProjected && (eastPlayIn.length > 0 || westPlayIn.length > 0)}
			<div class="playin-container">
				<h2>Play-In Tournament</h2>
				<div class="playin-grid">
					<div class="playin-conf">
						<div class="playin-conf-label">East</div>
						{#each eastPlayIn as team, i}
							<div class="playin-team" in:fly={{ x: -10, duration: 200, delay: i * 50 + 600 }}>
								<span class="seed">{team.playoff_rank}</span>
								<span class="team-name">{team.team_name}</span>
								<span class="team-record">{team.record}</span>
							</div>
						{/each}
					</div>
					<div class="playin-conf">
						<div class="playin-conf-label">West</div>
						{#each westPlayIn as team, i}
							<div class="playin-team" in:fly={{ x: 10, duration: 200, delay: i * 50 + 600 }}>
								<span class="seed">{team.playoff_rank}</span>
								<span class="team-name">{team.team_name}</span>
								<span class="team-record">{team.record}</span>
							</div>
						{/each}
					</div>
				</div>
			</div>
		{/if}
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

	/* 7-column grid: E-R1 | E-R2 | E-CF | Finals | W-CF | W-R2 | W-R1 */
	.bracket-container {
		display: grid;
		grid-template-columns: 1fr 1fr 1fr auto 1fr 1fr 1fr;
		grid-template-rows: auto 1fr;
		gap: 0.5rem;
		align-items: start;
	}

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

	.matchup {
		background: var(--bg-card);
		border: 1px solid var(--border-subtle);
		border-radius: var(--radius-sm);
		overflow: hidden;
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

	.team-record {
		font-size: 0.7rem;
		color: var(--text-muted);
		font-variant-numeric: tabular-nums;
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

	/* Play-In section */
	.playin-container {
		margin-top: 2.5rem;
		padding-top: 1.5rem;
		border-top: 1px dashed var(--border-subtle);
	}

	.playin-container h2 {
		text-align: center;
		font-size: 1.1rem;
		color: var(--text-secondary);
		margin-bottom: 1rem;
	}

	.playin-grid {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 2rem;
		max-width: 700px;
		margin: 0 auto;
	}

	.playin-conf-label {
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

	.error {
		text-align: center;
		padding: 3rem;
		color: var(--accent-red);
	}
</style>
