<script lang="ts">
	export let data: any[];
	export let columns: { key: string; label: string; format?: (v: any) => string }[];
	export let filterKey: string = '';

	let sortKey = '';
	let sortAsc = false;
	let search = '';

	$: filtered = search
		? data.filter(row => {
			const val = String(row[filterKey] || '').toLowerCase();
			return val.includes(search.toLowerCase());
		})
		: data;

	$: sorted = sortKey
		? [...filtered].sort((a, b) => {
			const va = a[sortKey];
			const vb = b[sortKey];
			if (typeof va === 'number' && typeof vb === 'number') {
				return sortAsc ? va - vb : vb - va;
			}
			return sortAsc
				? String(va).localeCompare(String(vb))
				: String(vb).localeCompare(String(va));
		})
		: filtered;

	function toggleSort(key: string) {
		if (sortKey === key) {
			sortAsc = !sortAsc;
		} else {
			sortKey = key;
			sortAsc = false;
		}
	}

	function fmt(col: typeof columns[0], val: any): string {
		if (col.format) return col.format(val);
		if (typeof val === 'number') {
			if (col.key.includes('pct')) return val.toFixed(3);
			if (Number.isInteger(val)) return String(val);
			return val.toFixed(1);
		}
		return String(val ?? '');
	}
</script>

<div class="search-bar">
	<input
		type="text"
		placeholder="Search..."
		bind:value={search}
		class="search-input"
	/>
	<span class="result-count">{sorted.length} results</span>
</div>

<div class="table-wrapper">
	<table>
		<thead>
			<tr>
				{#each columns as col}
					<th
						class:sortable={true}
						class:sorted={sortKey === col.key}
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
			{#each sorted as row}
				<tr>
					{#each columns as col}
						<td class:text-col={col.key === filterKey}>
							{fmt(col, row[col.key])}
						</td>
					{/each}
				</tr>
			{/each}
		</tbody>
	</table>
</div>

<style>
	.search-bar {
		display: flex;
		align-items: center;
		gap: 1rem;
		margin-bottom: 1rem;
	}

	.search-input {
		flex: 1;
		max-width: 320px;
		padding: 0.6rem 1rem;
		background: var(--bg-card);
		border: 1px solid var(--border-subtle);
		border-radius: var(--radius-sm);
		color: var(--text-primary);
		font-family: var(--font-body);
		font-size: 0.9rem;
		outline: none;
		transition: border-color var(--transition);
	}

	.search-input:focus {
		border-color: var(--accent-blue);
	}

	.search-input::placeholder {
		color: var(--text-muted);
	}

	.result-count {
		font-size: 0.8rem;
		color: var(--text-muted);
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
		text-align: right;
		white-space: nowrap;
		cursor: pointer;
		user-select: none;
		transition: color var(--transition);
	}

	th:hover, th.sorted { color: var(--accent-blue); }
	.sort-arrow { font-size: 0.6rem; margin-left: 0.2rem; }

	td {
		padding: 0.5rem 0.75rem;
		border-top: 1px solid var(--border-subtle);
		text-align: right;
		font-variant-numeric: tabular-nums;
	}

	td.text-col {
		text-align: left;
		font-weight: 500;
	}

	tr:hover td { background: var(--bg-card-hover); }
</style>
