<script lang="ts">
	import { onMount } from 'svelte';
	import { getPlayerStats, getTeamStats } from '$lib/api';
	import StatsTable from '$lib/components/StatsTable.svelte';
	import Skeleton from '$lib/components/Skeleton.svelte';
	import type { PlayerStats, TeamStats } from '$lib/types';

	let playerStats: PlayerStats[] = [];
	let teamStats: TeamStats[] = [];
	let loading = true;
	let error = '';
	let activeTab: 'players' | 'teams' = 'players';

	const playerColumns = [
		{ key: 'player_name', label: 'Player' },
		{ key: 'team_abbreviation', label: 'Team' },
		{ key: 'gp', label: 'GP' },
		{ key: 'mpg', label: 'MPG' },
		{ key: 'ppg', label: 'PPG' },
		{ key: 'rpg', label: 'RPG' },
		{ key: 'apg', label: 'APG' },
		{ key: 'spg', label: 'SPG' },
		{ key: 'bpg', label: 'BPG' },
		{ key: 'fg_pct', label: 'FG%' },
		{ key: 'fg3_pct', label: '3P%' },
		{ key: 'ft_pct', label: 'FT%' },
		{ key: 'plus_minus', label: '+/-', format: (v: number) => (v > 0 ? '+' : '') + v.toFixed(1) },
	];

	const teamColumns = [
		{ key: 'team_name', label: 'Team' },
		{ key: 'gp', label: 'GP' },
		{ key: 'wins', label: 'W' },
		{ key: 'losses', label: 'L' },
		{ key: 'ppg', label: 'PPG' },
		{ key: 'rpg', label: 'RPG' },
		{ key: 'apg', label: 'APG' },
		{ key: 'spg', label: 'SPG' },
		{ key: 'bpg', label: 'BPG' },
		{ key: 'fg_pct', label: 'FG%' },
		{ key: 'fg3_pct', label: '3P%' },
		{ key: 'ft_pct', label: 'FT%' },
		{ key: 'plus_minus', label: '+/-', format: (v: number) => (v > 0 ? '+' : '') + v.toFixed(1) },
	];

	onMount(async () => {
		try {
			const [ps, ts] = await Promise.all([getPlayerStats(), getTeamStats()]);
			playerStats = ps.sort((a, b) => b.ppg - a.ppg);
			teamStats = ts.sort((a, b) => b.ppg - a.ppg);
		} catch (e: any) {
			error = e.message || 'Failed to load stats';
		}
		loading = false;
	});
</script>

<div class="stats-page">
	<h1>Stats</h1>

	<div class="tabs">
		<button class="tab" class:active={activeTab === 'players'} on:click={() => activeTab = 'players'}>
			Player Stats
		</button>
		<button class="tab" class:active={activeTab === 'teams'} on:click={() => activeTab = 'teams'}>
			Team Stats
		</button>
	</div>

	{#if loading}
		<div class="skeleton-table">
			{#each Array(20) as _}
				<Skeleton width="100%" height="2rem" />
			{/each}
		</div>
	{:else if error}
		<div class="error">{error}</div>
	{:else if activeTab === 'players'}
		<StatsTable data={playerStats} columns={playerColumns} filterKey="player_name" />
	{:else}
		<StatsTable data={teamStats} columns={teamColumns} filterKey="team_name" />
	{/if}
</div>

<style>
	.stats-page h1 {
		font-size: 2rem;
		margin-bottom: 1.5rem;
		background: linear-gradient(135deg, var(--text-primary), var(--accent-orange));
		-webkit-background-clip: text;
		-webkit-text-fill-color: transparent;
		background-clip: text;
	}

	.tabs {
		display: flex;
		gap: 0.25rem;
		margin-bottom: 1.5rem;
		border-bottom: 1px solid var(--border-subtle);
	}

	.tab {
		padding: 0.75rem 1.5rem;
		font-weight: 600;
		font-size: 0.9rem;
		color: var(--text-secondary);
		border-bottom: 2px solid transparent;
		transition: all var(--transition);
		margin-bottom: -1px;
	}

	.tab:hover { color: var(--text-primary); }
	.tab.active { color: var(--accent-blue); border-bottom-color: var(--accent-blue); }

	.skeleton-table { display: flex; flex-direction: column; gap: 0.5rem; }
	.error { text-align: center; padding: 3rem; color: var(--accent-red); }
</style>
