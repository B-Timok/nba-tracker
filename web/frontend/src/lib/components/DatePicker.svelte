<script lang="ts">
	import { currentDate } from '$lib/stores';

	let showInput = false;
	let inputValue = '';

	function formatDisplay(dateStr: string): string {
		const d = new Date(dateStr + 'T12:00:00');
		const today = new Date();
		const todayStr = today.toISOString().split('T')[0];
		const label = dateStr === todayStr ? ' (Today)' : '';
		return d.toLocaleDateString('en-US', {
			weekday: 'short',
			month: 'short',
			day: 'numeric',
		}) + label;
	}

	function handleSubmit() {
		if (/^\d{4}-\d{2}-\d{2}$/.test(inputValue)) {
			currentDate.set(inputValue);
			showInput = false;
			inputValue = '';
		}
	}

	function handleKeydown(e: KeyboardEvent) {
		if (e.key === 'Escape') {
			showInput = false;
			inputValue = '';
		}
	}
</script>

<div class="date-picker">
	<button class="arrow" on:click={() => currentDate.prev()} aria-label="Previous day">
		◀
	</button>

	{#if showInput}
		<input
			type="date"
			bind:value={inputValue}
			on:change={handleSubmit}
			on:keydown={handleKeydown}
			on:blur={() => { showInput = false; inputValue = ''; }}
			class="date-input"
			autofocus
		/>
	{:else}
		<button class="date-display" on:click={() => { showInput = true; inputValue = $currentDate; }}>
			{formatDisplay($currentDate)}
		</button>
	{/if}

	<button class="arrow" on:click={() => currentDate.next()} aria-label="Next day">
		▶
	</button>
</div>

<style>
	.date-picker {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		margin-left: auto;
	}

	.arrow {
		width: 32px;
		height: 32px;
		display: flex;
		align-items: center;
		justify-content: center;
		border-radius: var(--radius-sm);
		font-size: 0.75rem;
		color: var(--text-secondary);
		transition: all var(--transition);
	}

	.arrow:hover {
		background: var(--bg-card);
		color: var(--accent-blue);
		transform: scale(1.1);
	}

	.arrow:active {
		transform: scale(0.95);
	}

	.date-display {
		padding: 0.4rem 1rem;
		border-radius: var(--radius-sm);
		font-size: 0.9rem;
		font-weight: 500;
		color: var(--text-primary);
		background: var(--bg-card);
		border: 1px solid var(--border-subtle);
		transition: all var(--transition);
		white-space: nowrap;
	}

	.date-display:hover {
		border-color: var(--accent-blue);
	}

	.date-input {
		padding: 0.4rem 0.75rem;
		border-radius: var(--radius-sm);
		font-size: 0.9rem;
		font-family: var(--font-body);
		color: var(--text-primary);
		background: var(--bg-card);
		border: 1px solid var(--accent-blue);
		outline: none;
		color-scheme: dark;
	}
</style>
