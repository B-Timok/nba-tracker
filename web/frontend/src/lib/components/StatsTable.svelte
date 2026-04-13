<script lang="ts">
	export let data: any[];
	export let columns: { key: string; label: string; format?: (v: any) => string }[];
	export let filterKey: string = '';
	export let highlightKey: string = '';
	export let pageSize: number = 50;

	let sortKey = '';
	let sortAsc = false;
	let search = '';
	let currentPage = 0;

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

	$: totalPages = Math.ceil(sorted.length / pageSize);
	$: paged = sorted.slice(currentPage * pageSize, (currentPage + 1) * pageSize);

	// Reset to page 0 when search or sort changes
	$: search, sortKey, sortAsc, currentPage = 0;

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
						class:highlighted={highlightKey === col.key}
						class:text-col={col.key === filterKey}
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
			{#each paged as row}
				<tr>
					{#each columns as col}
						<td class:text-col={col.key === filterKey} class:highlighted={highlightKey === col.key}>
							{fmt(col, row[col.key])}
						</td>
					{/each}
				</tr>
			{/each}
		</tbody>
	</table>
</div>

{#if totalPages > 1}
	<div class="pagination">
		<button class="page-btn" disabled={currentPage === 0} on:click={() => currentPage--}>
			← Prev
		</button>
		<span class="page-info">
			{currentPage * pageSize + 1}–{Math.min((currentPage + 1) * pageSize, sorted.length)} of {sorted.length}
		</span>
		<button class="page-btn" disabled={currentPage >= totalPages - 1} on:click={() => currentPage++}>
			Next →
		</button>
	</div>
{/if}

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
	th.text-col { text-align: left; }
	th.highlighted { color: var(--accent-orange); }
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

	td.highlighted {
		color: var(--accent-orange);
		font-weight: 600;
	}

	tr:hover td { background: var(--bg-card-hover); }

	.pagination {
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 1.5rem;
		margin-top: 1rem;
		padding: 0.75rem;
	}

	.page-btn {
		padding: 0.4rem 1rem;
		border-radius: var(--radius-sm);
		font-size: 0.85rem;
		font-weight: 600;
		color: var(--text-primary);
		background: var(--bg-card);
		border: 1px solid var(--border-subtle);
		transition: all 0.15s ease;
	}

	.page-btn:hover:not(:disabled) {
		border-color: var(--accent-orange);
		color: var(--accent-orange);
	}

	.page-btn:disabled {
		opacity: 0.3;
		cursor: default;
	}

	.page-info {
		font-size: 0.8rem;
		color: var(--text-muted);
		font-variant-numeric: tabular-nums;
	}
</style>
