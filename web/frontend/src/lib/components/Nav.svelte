<script lang="ts">
	import { page } from '$app/stores';
	import DatePicker from './DatePicker.svelte';

	const links = [
		{ href: '/', label: 'Scores' },
		{ href: '/standings', label: 'Standings' },
		{ href: '/stats', label: 'Stats' },
	];
</script>

<nav>
	<div class="nav-inner">
		<a href="/" class="logo">
			<span class="logo-icon">🏀</span>
			<span class="logo-text">NBA Scoreboard</span>
		</a>

		<div class="nav-links">
			{#each links as link}
				<a
					href={link.href}
					class="nav-link"
					class:active={$page.url.pathname === link.href}
				>
					{link.label}
				</a>
			{/each}
		</div>

		<DatePicker />
	</div>
</nav>

<style>
	nav {
		background: var(--bg-nav);
		border-bottom: 1px solid var(--border-subtle);
		position: sticky;
		top: 0;
		z-index: 100;
		backdrop-filter: blur(12px);
	}

	.nav-inner {
		max-width: 1200px;
		margin: 0 auto;
		padding: 0 1.5rem;
		height: 64px;
		display: flex;
		align-items: center;
		gap: 2rem;
	}

	.logo {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		font-family: var(--font-heading);
		font-size: 1.25rem;
		font-weight: 700;
		color: var(--text-primary);
		white-space: nowrap;
	}

	.logo:hover {
		color: var(--accent-orange);
	}

	.logo-icon {
		font-size: 1.5rem;
	}

	.nav-links {
		display: flex;
		gap: 0.25rem;
	}

	.nav-link {
		padding: 0.5rem 1rem;
		border-radius: var(--radius-sm);
		color: var(--text-secondary);
		font-weight: 500;
		font-size: 0.9rem;
		transition: all var(--transition);
	}

	.nav-link:hover {
		color: var(--text-primary);
		background: var(--bg-card);
	}

	.nav-link.active {
		color: var(--accent-blue);
		background: rgba(59, 130, 246, 0.1);
	}
</style>
