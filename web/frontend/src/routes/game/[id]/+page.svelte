<script lang="ts">
	import { page } from '$app/stores';
	import { onMount } from 'svelte';
	import { get } from 'svelte/store';
	import { getBoxScore, getPlayByPlay } from '$lib/api';
	import { selectedGame } from '$lib/stores';
	import BoxScore from '$lib/components/BoxScore.svelte';
	import PlayByPlay from '$lib/components/PlayByPlay.svelte';
	import Skeleton from '$lib/components/Skeleton.svelte';
	import type { BoxScoreResponse, PlayAction } from '$lib/types';

	let boxScore: BoxScoreResponse | null = null;
	let plays: PlayAction[] = [];
	let loading = true;
	let error = '';
	let activeTab: 'boxscore' | 'playbyplay' = 'boxscore';

	// Get game info from store (has records from scoreboard)
	const game = get(selectedGame);
	$: gameId = $page.params.id;

	onMount(async () => {
		try {
			const [bs, pbp] = await Promise.all([
				getBoxScore(gameId),
				getPlayByPlay(gameId),
			]);
			boxScore = bs;
			// Use records from the scoreboard game data if available
			if (game && boxScore) {
				boxScore.away.team.record = game.away_team.record;
				boxScore.away.team.wins = game.away_team.wins;
				boxScore.away.team.losses = game.away_team.losses;
				boxScore.home.team.record = game.home_team.record;
				boxScore.home.team.wins = game.home_team.wins;
				boxScore.home.team.losses = game.home_team.losses;
			}
			plays = pbp;
		} catch (e: any) {
			error = e.message || 'Failed to load game data';
		}
		loading = false;
	});
</script>

<div class="game-detail">
	<a href="/" class="back-link">← Back to Scores</a>

	{#if loading}
		<div class="score-header-skeleton">
			<Skeleton width="100%" height="6rem" />
		</div>
	{:else if error}
		<div class="error">{error}</div>
	{:else if boxScore}
		<div class="score-header">
			<div class="team-side away">
				<div class="team-name">{boxScore.away.team.city} {boxScore.away.team.name}</div>
				{#if boxScore.away.team.record !== '0-0'}
					<div class="team-record">{boxScore.away.team.record}</div>
				{/if}
				<div class="team-score" class:winning={boxScore.away.team.score > boxScore.home.team.score}>
					{boxScore.away.team.score}
				</div>
			</div>
			<div class="vs">—</div>
			<div class="team-side home">
				<div class="team-score" class:winning={boxScore.home.team.score > boxScore.away.team.score}>
					{boxScore.home.team.score}
				</div>
				<div class="team-name">{boxScore.home.team.city} {boxScore.home.team.name}</div>
				{#if boxScore.home.team.record !== '0-0'}
					<div class="team-record">{boxScore.home.team.record}</div>
				{/if}
			</div>
		</div>

		<div class="tabs">
			<button
				class="tab" class:active={activeTab === 'boxscore'}
				on:click={() => activeTab = 'boxscore'}
			>Box Score</button>
			<button
				class="tab" class:active={activeTab === 'playbyplay'}
				on:click={() => activeTab = 'playbyplay'}
			>Play-by-Play</button>
		</div>

		{#if activeTab === 'boxscore'}
			<div class="box-scores">
				<BoxScore team={boxScore.away} label="{boxScore.away.team.city} {boxScore.away.team.name}" teamTricode={boxScore.away.team.tricode} />
				<BoxScore team={boxScore.home} label="{boxScore.home.team.city} {boxScore.home.team.name}" teamTricode={boxScore.home.team.tricode} />
			</div>
		{:else}
			<PlayByPlay actions={plays} />
		{/if}
	{/if}
</div>

<style>
	.game-detail {
		max-width: 1000px;
		margin: 0 auto;
	}

	.back-link {
		display: inline-block;
		margin-bottom: 1rem;
		color: var(--text-secondary);
		font-size: 0.9rem;
		transition: color var(--transition);
	}

	.back-link:hover { color: var(--accent-blue); }

	.score-header {
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 2rem;
		padding: 2rem;
		background: var(--bg-card);
		border-radius: var(--radius);
		border: 1px solid var(--border-subtle);
		margin-bottom: 1.5rem;
	}

	.team-side {
		display: flex;
		align-items: center;
		gap: 1rem;
	}

	.team-side.away {
		flex-direction: row;
	}

	.team-side.home {
		flex-direction: row;
	}

	.team-name {
		font-family: var(--font-heading);
		font-size: 1.4rem;
		font-weight: 700;
		color: #ffffff;
	}

	.team-record {
		color: var(--text-muted);
		font-size: 0.9rem;
	}

	.team-score {
		font-family: var(--font-heading);
		font-size: 3rem;
		font-weight: 700;
	}

	.team-score.winning {
		color: var(--accent-orange);
	}

	.vs {
		font-size: 1.5rem;
		color: var(--text-muted);
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

	.tab:hover {
		color: var(--text-primary);
	}

	.tab.active {
		color: var(--text-primary);
		border-bottom-color: var(--accent-orange);
	}

	.box-scores {
		display: flex;
		flex-direction: column;
		gap: 2rem;
	}

	.error {
		text-align: center;
		padding: 3rem;
		color: var(--accent-red);
	}
</style>
