<script lang="ts">
	import type { TeamBoxScore } from '$lib/types';

	export let team: TeamBoxScore;
	export let label: string;

	let sortKey = '';
	let sortAsc = false;

	$: starters = team.players.filter(p => p.starter);
	$: bench = team.players.filter(p => !p.starter);
	$: allPlayers = [...starters, ...bench];
	$: sortedPlayers = sortKey
		? [...allPlayers].sort((a, b) => {
			const va = (a as any)[sortKey];
			const vb = (b as any)[sortKey];
			return sortAsc ? va - vb : vb - va;
		})
		: allPlayers;

	function toggleSort(key: string) {
		if (sortKey === key) {
			sortAsc = !sortAsc;
		} else {
			sortKey = key;
			sortAsc = false;
		}
	}

	const columns = [
		{ key: 'name', label: 'Player', align: 'left' },
		{ key: 'minutes', label: 'MIN', align: 'right' },
		{ key: 'points', label: 'PTS', align: 'right' },
		{ key: 'rebounds', label: 'REB', align: 'right' },
		{ key: 'assists', label: 'AST', align: 'right' },
		{ key: 'steals', label: 'STL', align: 'right' },
		{ key: 'blocks', label: 'BLK', align: 'right' },
		{ key: 'fg', label: 'FG', align: 'right' },
		{ key: 'fg3', label: '3PT', align: 'right' },
		{ key: 'ft', label: 'FT', align: 'right' },
		{ key: 'plus_minus', label: '+/-', align: 'right' },
	];
</script>

<div class="box-score">
	<h3>{label}</h3>
	<div class="table-wrapper">
		<table>
			<thead>
				<tr>
					{#each columns as col}
						<th
							class:sortable={col.key !== 'name' && col.key !== 'fg' && col.key !== 'fg3' && col.key !== 'ft'}
							class:sorted={sortKey === col.key}
							style="text-align: {col.align}"
							on:click={() => toggleSort(col.key)}
						>
							{col.label}
							{#if sortKey === col.key}
								<span class="sort-arrow">{sortAsc ? '▲' : '▼'}</span>
							{/if}
						</th>
					{/each}
				</tr>
			</thead>
			<tbody>
				{#each sortedPlayers as player, i}
					<tr class:starter={player.starter}>
						<td class="player-name">
							{player.name}
							{#if player.starter}
								<span class="starter-badge">S</span>
							{/if}
						</td>
						<td class="num">{player.minutes}</td>
						<td class="num highlight">{player.points}</td>
						<td class="num">{player.rebounds}</td>
						<td class="num">{player.assists}</td>
						<td class="num">{player.steals}</td>
						<td class="num">{player.blocks}</td>
						<td class="num">{player.fg}</td>
						<td class="num">{player.fg3}</td>
						<td class="num">{player.ft}</td>
						<td class="num" class:positive={player.plus_minus > 0} class:negative={player.plus_minus < 0}>
							{player.plus_minus > 0 ? '+' : ''}{player.plus_minus.toFixed(0)}
						</td>
					</tr>
				{/each}
				<tr class="totals-row">
					<td class="player-name">TOTALS</td>
					<td class="num"></td>
					<td class="num highlight">{team.totals.points}</td>
					<td class="num">{team.totals.rebounds}</td>
					<td class="num">{team.totals.assists}</td>
					<td class="num">{team.totals.steals}</td>
					<td class="num">{team.totals.blocks}</td>
					<td class="num">{team.totals.fg}</td>
					<td class="num">{team.totals.fg3}</td>
					<td class="num">{team.totals.ft}</td>
					<td class="num"></td>
				</tr>
			</tbody>
		</table>
	</div>
</div>

<style>
	.box-score h3 {
		margin-bottom: 0.75rem;
		font-size: 1.1rem;
	}

	.table-wrapper {
		overflow-x: auto;
		border-radius: var(--radius-sm);
		border: 1px solid var(--border-subtle);
	}

	table {
		width: 100%;
		border-collapse: collapse;
		font-size: 0.85rem;
	}

	th {
		padding: 0.6rem 0.75rem;
		background: var(--bg-card);
		font-weight: 600;
		font-size: 0.75rem;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		color: var(--text-secondary);
		white-space: nowrap;
		user-select: none;
	}

	th.sortable {
		cursor: pointer;
		transition: color var(--transition);
	}

	th.sortable:hover, th.sorted {
		color: var(--accent-blue);
	}

	.sort-arrow {
		font-size: 0.6rem;
		margin-left: 0.2rem;
	}

	td {
		padding: 0.5rem 0.75rem;
		border-top: 1px solid var(--border-subtle);
	}

	tr:hover td {
		background: var(--bg-card-hover);
	}

	.player-name {
		font-weight: 500;
		white-space: nowrap;
	}

	.starter-badge {
		font-size: 0.6rem;
		background: var(--accent-blue);
		color: white;
		padding: 0.1rem 0.3rem;
		border-radius: 3px;
		margin-left: 0.3rem;
		vertical-align: middle;
	}

	.num {
		text-align: right;
		font-variant-numeric: tabular-nums;
	}

	.highlight {
		font-weight: 700;
		color: var(--accent-orange);
	}

	.positive { color: var(--accent-green); }
	.negative { color: var(--accent-red); }

	.totals-row td {
		font-weight: 700;
		border-top: 2px solid var(--accent-blue);
		background: var(--bg-card);
	}
</style>
