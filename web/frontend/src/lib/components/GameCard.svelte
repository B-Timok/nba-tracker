<script lang="ts">
	import type { Game } from '$lib/types';
	import { getTeamColor } from '$lib/teamColors';
	import { selectedGame } from '$lib/stores';

	export let game: Game;

	$: statusClass = game.is_live ? 'live' : game.is_final ? 'final' : 'scheduled';
</script>

<a href="/game/{game.game_id}" class="card {statusClass}" on:click={() => selectedGame.set(game)}>
	<div class="status-badge">
		{#if game.is_live}
			<span class="live-dot"></span>
		{/if}
		{game.status_text}
	</div>

	<div class="teams">
		<div class="team away" style="--team-color: {getTeamColor(game.away_team.tricode)}">
			<span class="team-name">{game.away_team.city} {game.away_team.name}</span>
			<span class="record">{game.away_team.record}</span>
			<span class="score" class:winning={game.away_team.score > game.home_team.score}>
				{game.is_scheduled ? '' : game.away_team.score}
			</span>
		</div>
		<div class="team home" style="--team-color: {getTeamColor(game.home_team.tricode)}">
			<span class="team-name">{game.home_team.city} {game.home_team.name}</span>
			<span class="record">{game.home_team.record}</span>
			<span class="score" class:winning={game.home_team.score > game.away_team.score}>
				{game.is_scheduled ? '' : game.home_team.score}
			</span>
		</div>
	</div>

	{#if game.home_leader && !game.is_scheduled}
		<div class="leader">
			{game.home_leader.name} — {game.home_leader.points} PTS, {game.home_leader.rebounds} REB, {game.home_leader.assists} AST
		</div>
	{/if}
</a>

<style>
	.card {
		display: block;
		background: var(--bg-card);
		border: 1px solid var(--border-subtle);
		border-radius: var(--radius);
		padding: 1.25rem;
		transition: all var(--transition);
		cursor: pointer;
		text-decoration: none;
		color: var(--text-primary);
	}

	.card:hover {
		transform: translateY(-4px);
		box-shadow: 0 8px 30px rgba(0, 0, 0, 0.3);
		border-color: var(--accent-blue);
		background: var(--bg-card-hover);
	}

	.card:active {
		transform: translateY(-2px);
	}

	.card.live {
		border-color: var(--accent-green);
		box-shadow: 0 0 20px rgba(34, 197, 94, 0.1);
	}

	.card.live:hover {
		box-shadow: 0 0 30px rgba(34, 197, 94, 0.2);
		border-color: var(--accent-green);
	}

	.status-badge {
		display: flex;
		align-items: center;
		gap: 0.4rem;
		font-size: 0.75rem;
		font-weight: 600;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		margin-bottom: 0.75rem;
	}

	.live .status-badge { color: var(--accent-green); }
	.final .status-badge { color: var(--color-final); }
	.scheduled .status-badge { color: var(--color-scheduled); }

	.live-dot {
		width: 8px;
		height: 8px;
		border-radius: 50%;
		background: var(--accent-green);
		animation: pulse 1.5s ease-in-out infinite;
	}

	@keyframes pulse {
		0%, 100% { opacity: 1; transform: scale(1); }
		50% { opacity: 0.5; transform: scale(1.2); }
	}

	.teams {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.team {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		border-left: 3px solid var(--team-color);
		padding-left: 0.75rem;
	}

	.team-name {
		font-family: var(--font-heading);
		font-weight: 600;
		font-size: 1rem;
		flex: 1;
	}

	.record {
		font-size: 0.8rem;
		color: var(--text-muted);
	}

	.score {
		font-family: var(--font-heading);
		font-size: 1.5rem;
		font-weight: 700;
		min-width: 3rem;
		text-align: right;
	}

	.score.winning {
		color: var(--accent-orange);
	}

	.leader {
		margin-top: 0.75rem;
		padding-top: 0.75rem;
		border-top: 1px solid var(--border-subtle);
		font-size: 0.8rem;
		color: var(--text-secondary);
	}
</style>
