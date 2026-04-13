<script lang="ts">
	import { onDestroy } from 'svelte';
	import { fly } from 'svelte/transition';
	import { flip } from 'svelte/animate';
	import { currentDate } from '$lib/stores';
	import { getScoreboard } from '$lib/api';
	import GameCard from '$lib/components/GameCard.svelte';
	import Skeleton from '$lib/components/Skeleton.svelte';
	import type { Game } from '$lib/types';

	let games: Game[] = [];
	let loading = true;
	let error = '';
	let refreshTimer: ReturnType<typeof setInterval> | null = null;

	async function loadGames(date: string) {
		loading = true;
		error = '';
		try {
			games = await getScoreboard(date);
		} catch (e: any) {
			error = e.message || 'Failed to load games';
			games = [];
		}
		loading = false;
		manageAutoRefresh();
	}

	function manageAutoRefresh() {
		if (refreshTimer) {
			clearInterval(refreshTimer);
			refreshTimer = null;
		}
		const hasLive = games.some(g => g.is_live);
		if (hasLive) {
			refreshTimer = setInterval(() => loadGames($currentDate), 15000);
		}
	}

	const unsubscribe = currentDate.subscribe(date => {
		loadGames(date);
	});

	onDestroy(() => {
		unsubscribe();
		if (refreshTimer) clearInterval(refreshTimer);
	});
</script>

<div class="scoreboard">
	<h1>Scores</h1>

	{#if loading}
		<div class="grid">
			{#each Array(6) as _}
				<div class="skeleton-card">
					<Skeleton width="60px" height="0.75rem" />
					<div style="margin-top: 1rem">
						<Skeleton width="80%" height="1.25rem" />
					</div>
					<div style="margin-top: 0.5rem">
						<Skeleton width="80%" height="1.25rem" />
					</div>
				</div>
			{/each}
		</div>
	{:else if error}
		<div class="error">
			<p>{error}</p>
			<button class="retry-btn" on:click={() => loadGames($currentDate)}>Retry</button>
		</div>
	{:else if games.length === 0}
		<div class="empty">No games scheduled for this date.</div>
	{:else}
		<div class="grid">
			{#each games as game (game.game_id)}
				<div in:fly={{ y: 20, duration: 300 }} animate:flip={{ duration: 300 }}>
					<GameCard {game} />
				</div>
			{/each}
		</div>
	{/if}
</div>

<style>
	.scoreboard h1 {
		font-size: 2rem;
		margin-bottom: 1.5rem;
		background: linear-gradient(135deg, var(--text-primary), var(--accent-orange));
		-webkit-background-clip: text;
		-webkit-text-fill-color: transparent;
		background-clip: text;
	}

	.grid {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
		gap: 1rem;
	}

	.skeleton-card {
		background: var(--bg-card);
		border: 1px solid var(--border-subtle);
		border-radius: var(--radius);
		padding: 1.25rem;
	}

	.error {
		text-align: center;
		padding: 3rem;
		color: var(--accent-red);
	}

	.retry-btn {
		margin-top: 1rem;
		padding: 0.5rem 1.5rem;
		background: var(--accent-blue);
		color: white;
		border-radius: var(--radius-sm);
		font-weight: 600;
		transition: all var(--transition);
	}

	.retry-btn:hover {
		background: var(--accent-orange);
		transform: scale(1.05);
	}

	.empty {
		text-align: center;
		padding: 4rem;
		color: var(--text-muted);
		font-size: 1.1rem;
	}
</style>
