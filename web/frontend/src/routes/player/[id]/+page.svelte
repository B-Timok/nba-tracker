<script lang="ts">
	import { page } from '$app/stores';
	import { onMount } from 'svelte';
	import { fly } from 'svelte/transition';
	import { getPlayerProfile } from '$lib/api';
	import { getTeamColor } from '$lib/teamColors';
	import Skeleton from '$lib/components/Skeleton.svelte';
	import type { PlayerProfile } from '$lib/types';

	let profile: PlayerProfile | null = null;
	let loading = true;
	let error = '';

	$: playerId = parseInt($page.params.id);

	onMount(async () => {
		try {
			profile = await getPlayerProfile(playerId);
		} catch (e: any) {
			error = e.message || 'Failed to load player';
		}
		loading = false;
	});

	function formatBirthdate(dateStr: string): string {
		if (!dateStr) return '';
		const d = new Date(dateStr);
		return d.toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' });
	}

	function getAge(dateStr: string): number {
		if (!dateStr) return 0;
		const birth = new Date(dateStr);
		const now = new Date();
		let age = now.getFullYear() - birth.getFullYear();
		if (now.getMonth() < birth.getMonth() || (now.getMonth() === birth.getMonth() && now.getDate() < birth.getDate())) age--;
		return age;
	}

	function draftText(bio: any): string {
		if (!bio.draft_year || bio.draft_year === 'Undrafted') return 'Undrafted';
		return `${bio.draft_year} Round ${bio.draft_round}, Pick ${bio.draft_number}`;
	}
</script>

<div class="profile">
	<a href="/stats" class="back-link">← Back to Stats</a>

	{#if loading}
		<Skeleton width="100%" height="200px" />
	{:else if error}
		<div class="error">{error}</div>
	{:else if profile}
		{@const bio = profile.bio}
		{@const teamColor = getTeamColor(bio.team_abbreviation)}

		<div class="hero" style="border-top: 4px solid {teamColor}">
			<div class="hero-info">
				<div class="jersey" style="color: {teamColor}">#{bio.jersey}</div>
				<div class="name-block">
					<h1>{bio.display_name}</h1>
					<div class="team-line" style="color: {teamColor}">
						{bio.team_city} {bio.team_name} &middot; {bio.position}
					</div>
				</div>
			</div>

			<div class="headline-stats">
				<div class="stat-box">
					<div class="stat-value" style="color: {teamColor}">{profile.headline.pts}</div>
					<div class="stat-label">PPG</div>
				</div>
				<div class="stat-box">
					<div class="stat-value" style="color: {teamColor}">{profile.headline.reb}</div>
					<div class="stat-label">RPG</div>
				</div>
				<div class="stat-box">
					<div class="stat-value" style="color: {teamColor}">{profile.headline.ast}</div>
					<div class="stat-label">APG</div>
				</div>
			</div>
		</div>

		<div class="details-grid" in:fly={{ y: 20, duration: 300, delay: 100 }}>
			<div class="detail-card">
				<h3>Bio</h3>
				<div class="detail-row"><span class="label">Height</span><span>{bio.height}</span></div>
				<div class="detail-row"><span class="label">Weight</span><span>{bio.weight} lbs</span></div>
				<div class="detail-row"><span class="label">Born</span><span>{formatBirthdate(bio.birthdate)} (Age {getAge(bio.birthdate)})</span></div>
				<div class="detail-row"><span class="label">Country</span><span>{bio.country}</span></div>
				<div class="detail-row"><span class="label">Draft</span><span>{draftText(bio)}</span></div>
				<div class="detail-row"><span class="label">Experience</span><span>{parseInt(bio.to_year) - parseInt(bio.from_year) + 1} years</span></div>
			</div>
		</div>

		<div class="career-section" in:fly={{ y: 20, duration: 300, delay: 200 }}>
			<h2>Career Stats</h2>
			<div class="table-wrapper">
				<table>
					<thead>
						<tr>
							<th class="left">Season</th>
							<th class="left">Team</th>
							<th>GP</th>
							<th>GS</th>
							<th>MPG</th>
							<th>PPG</th>
							<th>RPG</th>
							<th>APG</th>
							<th>SPG</th>
							<th>BPG</th>
							<th>FG%</th>
							<th>3P%</th>
							<th>FT%</th>
						</tr>
					</thead>
					<tbody>
						{#each profile.seasons as season, i}
							<tr in:fly={{ x: -10, duration: 200, delay: i * 30 }}>
								<td class="left">{season.season}</td>
								<td class="left">{season.team_abbreviation}</td>
								<td>{season.gp}</td>
								<td>{season.gs}</td>
								<td>{season.mpg?.toFixed(1) ?? '-'}</td>
								<td class="highlight">{season.ppg?.toFixed(1) ?? '-'}</td>
								<td>{season.rpg?.toFixed(1) ?? '-'}</td>
								<td>{season.apg?.toFixed(1) ?? '-'}</td>
								<td>{season.spg?.toFixed(1) ?? '-'}</td>
								<td>{season.bpg?.toFixed(1) ?? '-'}</td>
								<td>{season.fg_pct != null ? (season.fg_pct * 100).toFixed(1) : '-'}</td>
								<td>{season.fg3_pct != null ? (season.fg3_pct * 100).toFixed(1) : '-'}</td>
								<td>{season.ft_pct != null ? (season.ft_pct * 100).toFixed(1) : '-'}</td>
							</tr>
						{/each}
						{#if profile.career_totals}
							<tr class="totals-row">
								<td class="left">Career</td>
								<td class="left"></td>
								<td>{profile.career_totals.gp}</td>
								<td>{profile.career_totals.gs}</td>
								<td>{profile.career_totals.mpg?.toFixed(1) ?? '-'}</td>
								<td class="highlight">{profile.career_totals.ppg?.toFixed(1) ?? '-'}</td>
								<td>{profile.career_totals.rpg?.toFixed(1) ?? '-'}</td>
								<td>{profile.career_totals.apg?.toFixed(1) ?? '-'}</td>
								<td>{profile.career_totals.spg?.toFixed(1) ?? '-'}</td>
								<td>{profile.career_totals.bpg?.toFixed(1) ?? '-'}</td>
								<td>{profile.career_totals.fg_pct != null ? (profile.career_totals.fg_pct * 100).toFixed(1) : '-'}</td>
								<td>{profile.career_totals.fg3_pct != null ? (profile.career_totals.fg3_pct * 100).toFixed(1) : '-'}</td>
								<td>{profile.career_totals.ft_pct != null ? (profile.career_totals.ft_pct * 100).toFixed(1) : '-'}</td>
							</tr>
						{/if}
					</tbody>
				</table>
			</div>
		</div>
	{/if}
</div>

<style>
	.profile {
		max-width: 1000px;
		margin: 0 auto;
	}

	.back-link {
		display: inline-block;
		margin-bottom: 1rem;
		color: var(--text-secondary);
		font-size: 0.9rem;
		transition: color 0.15s ease;
	}

	.back-link:hover { color: var(--accent-orange); }

	.hero {
		background: var(--bg-card);
		border: 1px solid var(--border-subtle);
		border-radius: var(--radius);
		padding: 2rem;
		margin-bottom: 1.5rem;
		display: flex;
		justify-content: space-between;
		align-items: center;
		gap: 2rem;
	}

	.hero-info {
		display: flex;
		align-items: center;
		gap: 1.5rem;
	}

	.jersey {
		font-family: var(--font-heading);
		font-size: 3rem;
		font-weight: 700;
		opacity: 0.8;
	}

	h1 {
		font-size: 2rem;
		color: #ffffff;
	}

	.team-line {
		font-size: 1rem;
		font-weight: 600;
		margin-top: 0.25rem;
	}

	.headline-stats {
		display: flex;
		gap: 2rem;
	}

	.stat-box {
		text-align: center;
	}

	.stat-value {
		font-family: var(--font-heading);
		font-size: 2rem;
		font-weight: 700;
	}

	.stat-label {
		font-size: 0.75rem;
		font-weight: 600;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		color: var(--text-muted);
		margin-top: 0.25rem;
	}

	.details-grid {
		margin-bottom: 1.5rem;
	}

	.detail-card {
		background: var(--bg-card);
		border: 1px solid var(--border-subtle);
		border-radius: var(--radius);
		padding: 1.5rem;
	}

	.detail-card h3 {
		margin-bottom: 1rem;
		font-size: 1rem;
		color: var(--text-secondary);
	}

	.detail-row {
		display: flex;
		justify-content: space-between;
		padding: 0.4rem 0;
		border-bottom: 1px solid var(--border-subtle);
		font-size: 0.9rem;
	}

	.detail-row:last-child { border-bottom: none; }

	.label {
		color: var(--text-muted);
	}

	.career-section h2 {
		font-size: 1.3rem;
		margin-bottom: 1rem;
		color: #ffffff;
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
	}

	th.left { text-align: left; }

	td {
		padding: 0.5rem 0.75rem;
		border-top: 1px solid var(--border-subtle);
		text-align: right;
		font-variant-numeric: tabular-nums;
	}

	td.left { text-align: left; }
	td.highlight { color: var(--accent-orange); font-weight: 600; }

	tr:hover td { background: var(--bg-card-hover); }

	.totals-row td {
		font-weight: 700;
		border-top: 2px solid var(--accent-orange);
		background: var(--bg-card);
	}

	.error {
		text-align: center;
		padding: 3rem;
		color: var(--accent-red);
	}
</style>
