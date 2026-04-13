import { writable } from 'svelte/store';
import type { Game } from '$lib/types';

function formatDate(d: Date): string {
	return d.toISOString().split('T')[0];
}

function createDateStore() {
	const { subscribe, set, update } = writable(formatDate(new Date()));

	return {
		subscribe,
		set: (dateStr: string) => set(dateStr),
		next: () => update(d => {
			const date = new Date(d + 'T12:00:00');
			date.setDate(date.getDate() + 1);
			return formatDate(date);
		}),
		prev: () => update(d => {
			const date = new Date(d + 'T12:00:00');
			date.setDate(date.getDate() - 1);
			return formatDate(date);
		}),
		today: () => set(formatDate(new Date())),
	};
}

export const currentDate = createDateStore();
export const selectedGame = writable<Game | null>(null);
