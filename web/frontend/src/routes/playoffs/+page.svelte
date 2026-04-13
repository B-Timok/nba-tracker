<script lang="ts">
	import { onMount } from 'svelte';
	import { fly } from 'svelte/transition';
	import { getPlayoffs } from '$lib/api';
	import { getTeamColor } from '$lib/teamColors';
	import Skeleton from '$lib/components/Skeleton.svelte';
	import type { PlayoffBracket, BracketSeries } from '$lib/types';

	let bracket: PlayoffBracket | null = null;
	let loading = true;
	let error = '';

	onMount(async () => {
		try {
			bracket = await getPlayoffs();
		} catch (e: any) {
			error = e.message || 'Failed to load playoff bracket';
		}
		loading = false;
	});

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
	<h1>Playoffs {bracket ? bracket.season : ''}</h1>

	{#if loading}
		<Skeleton width="100%" height="600px" />
	{:else if error}
		<div class="error">{error}</div>
	{:else if bracket}
		<div class="bracket-container">
			<!-- East Bracket: R1 → R2 → CF -->
			<div class="conference east">
				<div class="conf-label">Eastern Conference</div>
				<div class="rounds">
					{#each [1, 2, 3] as round}
						<div class="round round-{round}">
							{#each getSeriesByRoundConf(round, 'East') as series, i}
								<div class="matchup" in:fly={{ x: -20, duration: 300, delay: i * 100 + round * 150 }}>
									{#if hasTeams(series)}
										<div class="team-row" class:winner={isWinner(series, 'high')} class:loser={isLoser(series, 'high')} style="--team-color: {getTeamColor(series.high_seed.tricode)}">
											<span class="seed">{series.high_seed.rank}</span>
											<span class="team-name">{series.high_seed.city} {series.high_seed.name}</span>
											<span class="series-wins">{series.high_seed.wins}</span>
										</div>
										<div class="team-row" class:winner={isWinner(series, 'low')} class:loser={isLoser(series, 'low')} style="--team-color: {getTeamColor(series.low_seed.tricode)}">
											<span class="seed">{series.low_seed.rank}</span>
											<span class="team-name">{series.low_seed.city} {series.low_seed.name}</span>
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
				</div>
			</div>

			<!-- Finals -->
			<div class="finals">
				<div class="finals-label">NBA Finals</div>
				{#if finals && hasTeams(finals)}
					<div class="matchup finals-matchup" in:fly={{ y: -20, duration: 400, delay: 600 }}>
						<div class="team-row" class:winner={isWinner(finals, 'high')} class:loser={isLoser(finals, 'high')} style="--team-color: {getTeamColor(finals.high_seed.tricode)}">
							<span class="seed">{finals.high_seed.rank}</span>
							<span class="team-name">{finals.high_seed.city} {finals.high_seed.name}</span>
							<span class="series-wins">{finals.high_seed.wins}</span>
						</div>
						<div class="team-row" class:winner={isWinner(finals, 'low')} class:loser={isLoser(finals, 'low')} style="--team-color: {getTeamColor(finals.low_seed.tricode)}">
							<span class="seed">{finals.low_seed.rank}</span>
							<span class="team-name">{finals.low_seed.city} {finals.low_seed.name}</span>
							<span class="series-wins">{finals.low_seed.wins}</span>
						</div>
						<div class="series-status">{finals.series_text}</div>
					</div>
				{:else}
					<div class="matchup finals-matchup tbd-matchup">
						<div class="team-row tbd"><span class="team-name">East Champion</span></div>
						<div class="team-row tbd"><span class="team-name">West Champion</span></div>
					</div>
				{/if}
			</div>

			<!-- West Bracket: CF ← R2 ← R1 -->
			<div class="conference west">
				<div class="conf-label">Western Conference</div>
				<div class="rounds">
					{#each [3, 2, 1] as round}
						<div class="round round-{round}">
							{#each getSeriesByRoundConf(round, 'West') as series, i}
								<div class="matchup" in:fly={{ x: 20, duration: 300, delay: i * 100 + (4 - round) * 150 }}>
									{#if hasTeams(series)}
										<div class="team-row" class:winner={isWinner(series, 'high')} class:loser={isLoser(series, 'high')} style="--team-color: {getTeamColor(series.high_seed.tricode)}">
											<span class="seed">{series.high_seed.rank}</span>
											<span class="team-name">{series.high_seed.city} {series.high_seed.name}</span>
											<span class="series-wins">{series.high_seed.wins}</span>
										</div>
										<div class="team-row" class:winner={isWinner(series, 'low')} class:loser={isLoser(series, 'low')} style="--team-color: {getTeamColor(series.low_seed.tricode)}">
											<span class="seed">{series.low_seed.rank}</span>
											<span class="team-name">{series.low_seed.city} {series.low_seed.name}</span>
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
				</div>
			</div>
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
		margin-bottom: 2rem;
		text-align: center;
		background: linear-gradient(135deg, var(--text-primary), var(--accent-orange));
		-webkit-background-clip: text;
		-webkit-text-fill-color: transparent;
		background-clip: text;
	}

	.bracket-container {
		display: grid;
		grid-template-columns: 1fr auto 1fr;
		gap: 1rem;
		align-items: start;
	}

	.conference {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.conf-label {
		font-family: var(--font-heading);
		font-size: 1rem;
		font-weight: 700;
		color: var(--text-secondary);
		text-transform: uppercase;
		letter-spacing: 0.1em;
		text-align: center;
		margin-bottom: 0.5rem;
	}

	.rounds {
		display: flex;
		gap: 0.75rem;
	}

	.west .rounds {
		flex-direction: row-reverse;
	}

	.round {
		display: flex;
		flex-direction: column;
		justify-content: space-around;
		gap: 1rem;
		flex: 1;
		min-width: 0;
	}

	.round-1 { min-height: 500px; }
	.round-2 { min-height: 500px; }
	.round-3 { min-height: 500px; }

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
		overflow: hidden;
		text-overflow: ellipsis;
	}

	.tbd .team-name {
		color: var(--text-muted);
		font-style: italic;
	}

	.series-wins {
		font-family: var(--font-heading);
		font-size: 1rem;
		font-weight: 700;
		min-width: 1.5rem;
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

	.finals {
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		min-height: 500px;
		gap: 1rem;
	}

	.finals-label {
		font-family: var(--font-heading);
		font-size: 1.2rem;
		font-weight: 700;
		color: var(--accent-orange);
		text-transform: uppercase;
		letter-spacing: 0.1em;
	}

	.finals-matchup {
		min-width: 220px;
	}

	.finals-matchup .team-name {
		font-size: 0.9rem;
	}

	.finals-matchup .series-wins {
		font-size: 1.2rem;
	}

	.error {
		text-align: center;
		padding: 3rem;
		color: var(--accent-red);
	}
</style>
