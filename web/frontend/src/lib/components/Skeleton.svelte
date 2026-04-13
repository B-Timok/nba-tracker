<script lang="ts">
	export let width: string = '100%';
	export let height: string = '1rem';
	export let rounded: boolean = false;
</script>

<div
	class="skeleton"
	class:rounded
	style="width: {width}; height: {height}"
/>

<style>
	.skeleton {
		background: linear-gradient(
			90deg,
			var(--bg-card) 25%,
			var(--bg-card-hover) 50%,
			var(--bg-card) 75%
		);
		background-size: 200% 100%;
		animation: shimmer 1.5s ease-in-out infinite;
		border-radius: var(--radius-sm);
	}

	.rounded {
		border-radius: 50%;
	}

	@keyframes shimmer {
		0% { background-position: 200% 0; }
		100% { background-position: -200% 0; }
	}
</style>
