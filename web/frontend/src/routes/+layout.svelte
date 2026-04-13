<script lang="ts">
	import '../app.css';
	import Nav from '$lib/components/Nav.svelte';
	import { fly, fade } from 'svelte/transition';
	import { page } from '$app/stores';

	$: key = $page.url.pathname;
	$: isWide = $page.url.pathname === '/playoffs';
</script>

<Nav />

<main class:wide={isWide}>
	{#key key}
		<div class="page" in:fly={{ y: 20, duration: 300, delay: 150 }} out:fade={{ duration: 150 }}>
			<slot />
		</div>
	{/key}
</main>

<style>
	main {
		max-width: 1200px;
		margin: 0 auto;
		padding: 1.5rem;
		min-height: calc(100vh - 64px);
	}

	main.wide {
		max-width: 100%;
		padding: 1.5rem 1rem;
	}

	.page {
		width: 100%;
	}
</style>
