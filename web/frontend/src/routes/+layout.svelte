<script lang="ts">
	import '../app.css';
	import Nav from '$lib/components/Nav.svelte';
	import { fly, fade } from 'svelte/transition';
	import { page } from '$app/stores';

	$: key = $page.url.pathname;
</script>

<Nav />

<main>
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

	.page {
		width: 100%;
	}
</style>
