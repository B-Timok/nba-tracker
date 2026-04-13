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
	let activeView: 'players' | 'teams' = 'players';
	let activeCategory = 'ppg';

	const categories = [
		{ key: 'ppg', label: 'Points' },
		{ key: 'rpg', label: 'Rebounds' },
		{ key: 'apg', label: 'Assists' },
		{ key: 'spg', label: 'Steals' },
		{ key: 'bpg', label: 'Blocks' },
		{ key: 'fg_pct', label: 'FG%' },
		{ key: 'fg3_pct', label: '3P%' },
		{ key: 'ft_pct', label: 'FT%' },
	];

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

	$: sortedPlayers = [...playerStats].sort((a, b) => {
		const va = (a as any)[activeCategory];
		const vb = (b as any)[activeCategory];
		return vb - va;
	});

	$: sortedTeams = [...teamStats].sort((a, b) => {
		const va = (a as any)[activeCategory];
		const vb = (b as any)[activeCategory];
		return vb - va;
	});

	onMount(async () => {
		try {
			const [ps, ts] = await Promise.all([getPlayerStats(), getTeamStats()]);
			playerStats = ps;
			teamStats = ts;
		} catch (e: any) {
			error = e.message || 'Failed to load stats';
		}
		loading = false;
	});
</script>

<div class="stats-page">
	<h1>Stats</h1>

	<div class="tabs">
		<button class="tab" class:active={activeView === 'players'} on:click={() => activeView = 'players'}>
			Player Stats
		</button>
		<button class="tab" class:active={activeView === 'teams'} on:click={() => activeView = 'teams'}>
			Team Stats
		</button>
	</div>

	<div class="categories">
		{#each categories as cat}
			<button
				class="cat-btn"
				class:active={activeCategory === cat.key}
				on:click={() => activeCategory = cat.key}
			>
				{cat.label}
			</button>
		{/each}
	</div>

	{#if loading}
		<div class="skeleton-table">
			{#each Array(20) as _}
				<Skeleton width="100%" height="2rem" />
			{/each}
		</div>
	{:else if error}
		<div class="error">{error}</div>
	{:else if activeView === 'players'}
		<StatsTable data={sortedPlayers} columns={playerColumns} filterKey="player_name" />
	{:else}
		<StatsTable data={sortedTeams} columns={teamColumns} filterKey="team_name" />
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
		margin-bottom: 1rem;
		border-bottom: 1px solid var(--border-subtle);
	}

	.tab {
		padding: 0.75rem 1.5rem;
		font-weight: 600;
		font-size: 0.9rem;
		color: var(--text-secondary);
		border-bottom: 2px solid transparent;
		transition: all 0.15s ease;
		margin-bottom: -1px;
	}

	.tab:hover { color: var(--text-primary); }
	.tab.active { color: var(--text-primary); border-bottom-color: var(--accent-orange); }

	.categories {
		display: flex;
		flex-wrap: wrap;
		gap: 0.5rem;
		margin-bottom: 1.5rem;
	}

	.cat-btn {
		padding: 0.4rem 1rem;
		border-radius: 999px;
		font-size: 0.8rem;
		font-weight: 600;
		color: var(--text-muted);
		background: var(--bg-card);
		border: 1px solid var(--border-subtle);
		transition: all 0.15s ease;
	}

	.cat-btn:hover {
		color: var(--text-primary);
		border-color: var(--text-muted);
	}

	.cat-btn.active {
		color: #ffffff;
		background: var(--accent-orange);
		border-color: var(--accent-orange);
	}

	.skeleton-table { display: flex; flex-direction: column; gap: 0.5rem; }
	.error { text-align: center; padding: 3rem; color: var(--accent-red); }
</style>
