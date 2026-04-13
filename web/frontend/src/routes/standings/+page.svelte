<script lang="ts">
	import { onMount } from 'svelte';
	import { fly } from 'svelte/transition';
	import { getStandings } from '$lib/api';
	import Skeleton from '$lib/components/Skeleton.svelte';
	import type { StandingsEntry } from '$lib/types';

	let entries: StandingsEntry[] = [];
	let loading = true;
	let error = '';
	let activeConf: 'East' | 'West' = 'East';

	onMount(async () => {
		try {
			entries = await getStandings();
		} catch (e: any) {
			error = e.message || 'Failed to load standings';
		}
		loading = false;
	});

	$: filtered = entries
		.filter(e => e.conference === activeConf)
		.sort((a, b) => a.playoff_rank - b.playoff_rank);
</script>

<div class="standings-page">
	<h1>Standings</h1>

	<div class="tabs">
		<button class="tab" class:active={activeConf === 'East'} on:click={() => activeConf = 'East'}>
			Eastern Conference
		</button>
		<button class="tab" class:active={activeConf === 'West'} on:click={() => activeConf = 'West'}>
			Western Conference
		</button>
	</div>

	{#if loading}
		<div class="skeleton-table">
			{#each Array(15) as _}
				<Skeleton width="100%" height="2.5rem" />
			{/each}
		</div>
	{:else if error}
		<div class="error">{error}</div>
	{:else}
		<div class="table-wrapper">
			<table>
				<thead>
					<tr>
						<th class="rank">#</th>
						<th class="team-col">Team</th>
						<th>W</th>
						<th>L</th>
						<th>PCT</th>
						<th>GB</th>
						<th>Home</th>
						<th>Road</th>
						<th>L10</th>
						<th>Streak</th>
					</tr>
				</thead>
				<tbody>
					{#each filtered as entry, i}
						<tr in:fly={{ x: -20, duration: 200, delay: i * 30 }} class:playoff-line={entry.playoff_rank === 6} class:playin-line={entry.playoff_rank === 10}>
							<td class="rank">{entry.playoff_rank}</td>
							<td class="team-col">
								<span class="team-name">{entry.team_city} {entry.team_name}</span>
								{#if entry.clinch_indicator?.trim()}
									<span class="clinch">{entry.clinch_indicator.trim()}</span>
								{/if}
							</td>
							<td>{entry.wins}</td>
							<td>{entry.losses}</td>
							<td>{entry.win_pct.toFixed(3)}</td>
							<td>{entry.games_back > 0 ? entry.games_back : '—'}</td>
							<td>{entry.home_record}</td>
							<td>{entry.road_record}</td>
							<td>{entry.last_10}</td>
							<td class:streak-w={entry.streak.startsWith('W')} class:streak-l={entry.streak.startsWith('L')}>
								{entry.streak}
							</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>

		<div class="legend">
			<span class="legend-title">Key:</span>
			<span><strong>w</strong> — best overall record</span>
			<span><strong>x</strong> — clinched playoff</span>
			<span><strong>p/pi</strong> — clinched play-in</span>
			<span><strong>a/c/se/sw/nw/pac</strong> — clinched division</span>
			<span><strong>o</strong> — eliminated from playoffs</span>
			<span><strong>e</strong> — eliminated from contention</span>
		</div>
	{/if}
</div>

<style>
	.standings-page h1 {
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
	.tab.active { color: var(--text-primary); border-bottom-color: var(--accent-orange); }

	.table-wrapper {
		overflow-x: auto;
		border-radius: var(--radius-sm);
		border: 1px solid var(--border-subtle);
	}

	table {
		width: 100%;
		border-collapse: collapse;
		font-size: 0.9rem;
	}

	th {
		padding: 0.75rem;
		background: var(--bg-card);
		font-weight: 600;
		font-size: 0.75rem;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		color: var(--text-secondary);
		text-align: right;
	}

	th.rank, th.team-col { text-align: left; }

	td {
		padding: 0.6rem 0.75rem;
		border-top: 1px solid var(--border-subtle);
		text-align: right;
		font-variant-numeric: tabular-nums;
	}

	td.rank { text-align: left; font-weight: 700; color: var(--text-muted); }
	td.team-col { text-align: left; }

	tr:hover td { background: var(--bg-card-hover); }

	tr.playoff-line td { border-bottom: 2px solid var(--accent-blue); }
	tr.playin-line td { border-bottom: 2px solid var(--accent-red); }

	.team-name { font-weight: 600; }
	.clinch { font-size: 0.7rem; color: var(--accent-green); margin-left: 0.3rem; }
	.streak-w { color: var(--accent-green); }
	.streak-l { color: var(--accent-red); }

	.legend {
		display: flex;
		flex-wrap: wrap;
		gap: 1rem;
		margin-top: 1rem;
		padding: 0.75rem 1rem;
		background: var(--bg-card);
		border: 1px solid var(--border-subtle);
		border-radius: var(--radius-sm);
		font-size: 0.75rem;
		color: var(--text-muted);
	}

	.legend-title {
		font-weight: 600;
		color: var(--text-secondary);
	}

	.legend strong {
		color: var(--accent-green);
	}

	.skeleton-table { display: flex; flex-direction: column; gap: 0.5rem; }
	.error { text-align: center; padding: 3rem; color: var(--accent-red); }
</style>
