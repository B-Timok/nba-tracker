<script lang="ts">
	import type { PlayAction } from '$lib/types';
	import { fly } from 'svelte/transition';

	export let actions: PlayAction[];

	function formatClock(clock: string): string {
		const match = clock.match(/PT(\d+)M([\d.]+)S/);
		if (match) {
			const mins = parseInt(match[1]);
			const secs = Math.floor(parseFloat(match[2]));
			return `${mins}:${secs.toString().padStart(2, '0')}`;
		}
		return clock;
	}

	function periodLabel(period: number): string {
		return period <= 4 ? `Q${period}` : `OT${period - 4}`;
	}

	// Group actions by period
	$: grouped = actions.reduce((acc, action) => {
		if (!action.description) return acc;
		const key = action.period;
		if (!acc[key]) acc[key] = [];
		acc[key].push(action);
		return acc;
	}, {} as Record<number, PlayAction[]>);

	$: periods = Object.keys(grouped).map(Number).sort((a, b) => a - b);
</script>

<div class="pbp">
	{#each periods as period}
		<div class="period-section">
			<div class="period-header">{periodLabel(period)}</div>
			{#each grouped[period] as action, i}
				<div
					class="play"
					class:field-goal={action.is_field_goal}
					in:fly={{ x: -10, duration: 200, delay: i * 10 }}
				>
					<span class="clock">{formatClock(action.clock)}</span>
					<span class="team-tri" class:has-team={!!action.team_tricode}>
						{action.team_tricode || ''}
					</span>
					<span class="score">
						{action.score_away}-{action.score_home}
					</span>
					<span class="desc">{action.description}</span>
				</div>
			{/each}
		</div>
	{/each}
</div>

<style>
	.pbp {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.period-header {
		font-family: var(--font-heading);
		font-weight: 700;
		font-size: 1rem;
		color: var(--accent-blue);
		padding: 0.75rem 0;
		border-bottom: 2px solid var(--accent-blue);
		margin-top: 1rem;
	}

	.period-section:first-child .period-header {
		margin-top: 0;
	}

	.play {
		display: flex;
		align-items: baseline;
		gap: 0.75rem;
		padding: 0.4rem 0.5rem;
		border-radius: var(--radius-sm);
		font-size: 0.85rem;
		transition: background var(--transition);
	}

	.play:hover {
		background: var(--bg-card);
	}

	.play.field-goal {
		background: rgba(255, 255, 255, 0.03);
	}

	.clock {
		font-variant-numeric: tabular-nums;
		color: var(--text-muted);
		min-width: 3rem;
		text-align: right;
	}

	.team-tri {
		font-weight: 700;
		min-width: 2.5rem;
		color: var(--accent-orange);
	}

	.team-tri:not(.has-team) {
		color: transparent;
	}

	.score {
		font-variant-numeric: tabular-nums;
		color: var(--text-secondary);
		min-width: 4rem;
	}

	.desc {
		flex: 1;
		color: var(--text-primary);
	}
</style>
