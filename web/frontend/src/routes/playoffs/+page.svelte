<script lang="ts">
	import { onMount } from 'svelte';
	import { fly } from 'svelte/transition';
	import { getStandings, getPlayoffs, getPlayIn } from '$lib/api';
	import { getTeamColor } from '$lib/teamColors';
	import Skeleton from '$lib/components/Skeleton.svelte';
	import type { StandingsEntry, PlayoffBracket, BracketSeries, BracketTeam, PlayInGame } from '$lib/types';

	const tricodeByName: Record<string, string> = {
		'Hawks': 'ATL', 'Celtics': 'BOS', 'Nets': 'BKN', 'Hornets': 'CHA',
		'Bulls': 'CHI', 'Cavaliers': 'CLE', 'Mavericks': 'DAL', 'Nuggets': 'DEN',
		'Pistons': 'DET', 'Warriors': 'GSW', 'Rockets': 'HOU', 'Pacers': 'IND',
		'Clippers': 'LAC', 'Lakers': 'LAL', 'Grizzlies': 'MEM', 'Heat': 'MIA',
		'Bucks': 'MIL', 'Timberwolves': 'MIN', 'Pelicans': 'NOP', 'Knicks': 'NYK',
		'Thunder': 'OKC', 'Magic': 'ORL', '76ers': 'PHI', 'Suns': 'PHX',
		'Trail Blazers': 'POR', 'Kings': 'SAC', 'Spurs': 'SAS', 'Raptors': 'TOR',
		'Jazz': 'UTA', 'Wizards': 'WAS',
	};

	function entryTricode(e: StandingsEntry): string {
		return tricodeByName[e.team_name] || e.team_name.substring(0, 3).toUpperCase();
	}

	type PlayInResult = {
		sevenSeed: StandingsEntry;
		eightSeed: StandingsEntry | null;      // null when #8 game hasn't happened yet
		eightCandidates: StandingsEntry[];      // teams still alive for #8 (size 0, 1, or 2)
		eliminated: Set<string>;                 // tricodes eliminated in play-in
		games: Array<PlayInGame & {
			label: string;
			home_name: string; home_seed: number;
			away_name: string; away_seed: number;
		}>;
	};

	function computePlayInResult(entries: StandingsEntry[], games: PlayInGame[], conf: 'East' | 'West'): PlayInResult {
		const seeds = entries
			.filter(e => e.conference === conf)
			.sort((a, b) => a.playoff_rank - b.playoff_rank)
			.slice(6, 10);
		const byTricode = new Map<string, StandingsEntry>(seeds.map(e => [entryTricode(e), e]));
		const allTricodes = new Set(byTricode.keys());

		const confGames = games
			.filter(g => allTricodes.has(g.home_tricode) && allTricodes.has(g.away_tricode))
			.sort((a, b) => a.date.localeCompare(b.date) || a.game_id.localeCompare(b.game_id));

		let sevenSeed: StandingsEntry = seeds[0];   // default: original #7
		let sevenLoser: StandingsEntry | null = null;
		let tenWinner: StandingsEntry | null = null;
		let eightSeed: StandingsEntry | null = null;
		const eliminated = new Set<string>();
		const labeled: PlayInResult['games'] = [];

		for (const g of confGames) {
			const home = byTricode.get(g.home_tricode)!;
			const away = byTricode.get(g.away_tricode)!;
			const matchRanks = [home.playoff_rank, away.playoff_rank].sort((a, b) => a - b);

			let label: string;
			if (matchRanks[0] === 7 && matchRanks[1] === 8) label = '7 vs 8 — winner is #7';
			else if (matchRanks[0] === 9 && matchRanks[1] === 10) label = '9 vs 10 — loser eliminated';
			else label = '#8 seed decider';

			if (g.status === 3) {
				const winner = g.home_score > g.away_score ? home : away;
				const loser = g.home_score > g.away_score ? away : home;
				const loserTC = loser === home ? g.home_tricode : g.away_tricode;
				if (label.startsWith('7 vs 8')) { sevenSeed = winner; sevenLoser = loser; }
				else if (label.startsWith('9 vs 10')) { tenWinner = winner; eliminated.add(loserTC); }
				else { eightSeed = winner; eliminated.add(loserTC); }
			}
			labeled.push({
				...g,
				label,
				home_name: home.team_name, home_seed: home.playoff_rank,
				away_name: away.team_name, away_seed: away.playoff_rank,
			});
		}

		const eightCandidates: StandingsEntry[] = eightSeed
			? []
			: [sevenLoser, tenWinner].filter((e): e is StandingsEntry => e !== null);
		// Before any play-in has happened, default #8 to the original #8 seed
		if (!eightSeed && eightCandidates.length === 0) {
			eightSeed = seeds[1] ?? null;
		}

		return { sevenSeed, eightSeed, eightCandidates, eliminated, games: labeled };
	}

	function tbdTeam(rank: number, candidates: StandingsEntry[]): BracketTeam {
		const name = candidates.length === 2
			? `${candidates[0].team_name} / ${candidates[1].team_name}`
			: candidates.length === 1
				? `${candidates[0].team_name} or TBD`
				: 'TBD';
		return { team_id: -1, city: '', name, tricode: '', rank, wins: 0, reg_wins: 0, reg_losses: 0 };
	}

	const arenas: Record<string, string> = {
		'Atlanta': 'State Farm Arena, Atlanta',
		'Boston': 'TD Garden, Boston',
		'Brooklyn': 'Barclays Center, Brooklyn',
		'Charlotte': 'Spectrum Center, Charlotte',
		'Chicago': 'United Center, Chicago',
		'Cleveland': 'Rocket Mortgage FieldHouse, Cleveland',
		'Dallas': 'American Airlines Center, Dallas',
		'Denver': 'Ball Arena, Denver',
		'Detroit': 'Little Caesars Arena, Detroit',
		'Golden State': 'Chase Center, San Francisco',
		'Houston': 'Toyota Center, Houston',
		'Indiana': 'Gainbridge Fieldhouse, Indianapolis',
		'Los Angeles': 'Crypto.com Arena, Los Angeles',
		'Memphis': 'FedExForum, Memphis',
		'Miami': 'Kaseya Center, Miami',
		'Milwaukee': 'Fiserv Forum, Milwaukee',
		'Minnesota': 'Target Center, Minneapolis',
		'New Orleans': 'Smoothie King Center, New Orleans',
		'New York': 'Madison Square Garden, New York',
		'Oklahoma City': 'Paycom Center, Oklahoma City',
		'Orlando': 'Kia Center, Orlando',
		'Philadelphia': 'Wells Fargo Center, Philadelphia',
		'Phoenix': 'Footprint Center, Phoenix',
		'Portland': 'Moda Center, Portland',
		'Sacramento': 'Golden 1 Center, Sacramento',
		'San Antonio': 'Frost Bank Center, San Antonio',
		'Toronto': 'Scotiabank Arena, Toronto',
		'Utah': 'Delta Center, Salt Lake City',
		'Washington': 'Capital One Arena, Washington',
	};

	let loading = true;
	let error = '';
	let isProjected = false;
	let seasonLabel = '';

	let allSeries: BracketSeries[] = [];
	let eastResult: PlayInResult | null = null;
	let westResult: PlayInResult | null = null;

	function entryToBracketTeam(e: StandingsEntry, overrideRank?: number): BracketTeam {
		return {
			team_id: e.team_id,
			city: e.team_city,
			name: e.team_name,
			tricode: entryTricode(e),
			rank: overrideRank ?? e.playoff_rank,
			wins: 0,
			reg_wins: e.wins,
			reg_losses: e.losses,
		};
	}

	function buildProjectedBracket(entries: StandingsEntry[], playIn: PlayInGame[]) {
		const series: BracketSeries[] = [];
		let orderCounter = 1;

		for (const conf of ['East', 'West'] as const) {
			const teams = entries
				.filter(e => e.conference === conf)
				.sort((a, b) => a.playoff_rank - b.playoff_rank);

			const result = computePlayInResult(entries, playIn, conf);
			if (conf === 'East') eastResult = result; else westResult = result;

			const sevenBracket = entryToBracketTeam(result.sevenSeed, 7);
			const eightBracket: BracketTeam = result.eightSeed
				? entryToBracketTeam(result.eightSeed, 8)
				: tbdTeam(8, result.eightCandidates);
			const top8: BracketTeam[] = [
				...teams.slice(0, 6).map(e => entryToBracketTeam(e)),
				sevenBracket,
				eightBracket,
			];

			const pairings = [[0, 7], [1, 6], [2, 5], [3, 4]];
			for (const [hi, lo] of pairings) {
				series.push({
					series_id: `proj-${conf}-r1-${orderCounter}`,
					round: 1,
					series_number: orderCounter,
					conference: conf,
					round_name: 'First Round',
					series_text: '',
					series_status: 0,
					series_winner: 0,
					high_seed: top8[hi],
					low_seed: top8[lo],
					display_order: orderCounter,
				});
				orderCounter++;
			}

			for (let i = 0; i < 2; i++) {
				series.push({
					series_id: `proj-${conf}-r2-${orderCounter}`,
					round: 2, series_number: orderCounter, conference: conf,
					round_name: 'Conf. Semis', series_text: '', series_status: 0, series_winner: 0,
					high_seed: { team_id: 0, city: '', name: '', tricode: '', rank: 0, wins: 0, reg_wins: 0, reg_losses: 0 },
					low_seed: { team_id: 0, city: '', name: '', tricode: '', rank: 0, wins: 0, reg_wins: 0, reg_losses: 0 },
					display_order: orderCounter,
				});
				orderCounter++;
			}

			series.push({
				series_id: `proj-${conf}-r3-${orderCounter}`,
				round: 3, series_number: orderCounter, conference: conf,
				round_name: 'Conf. Finals', series_text: '', series_status: 0, series_winner: 0,
				high_seed: { team_id: 0, city: '', name: '', tricode: '', rank: 0, wins: 0, reg_wins: 0, reg_losses: 0 },
				low_seed: { team_id: 0, city: '', name: '', tricode: '', rank: 0, wins: 0, reg_wins: 0, reg_losses: 0 },
				display_order: orderCounter,
			});
			orderCounter++;
		}

		series.push({
			series_id: 'proj-finals',
			round: 4, series_number: orderCounter, conference: '',
			round_name: 'NBA Finals', series_text: '', series_status: 0, series_winner: 0,
			high_seed: { team_id: 0, city: '', name: '', tricode: '', rank: 0, wins: 0, reg_wins: 0, reg_losses: 0 },
			low_seed: { team_id: 0, city: '', name: '', tricode: '', rank: 0, wins: 0, reg_wins: 0, reg_losses: 0 },
			display_order: orderCounter,
		});

		allSeries = series;
	}

	onMount(async () => {
		try {
			try {
				const bracket = await getPlayoffs();
				const now = new Date();
				const currentSeasonStart = now.getMonth() >= 8 ? now.getFullYear() : now.getFullYear() - 1;
				const currentSeason = `${currentSeasonStart}-${String(currentSeasonStart + 1).slice(-2)}`;
				const isCurrentSeason = bracket.season === currentSeason;
				const hasActiveSeries = bracket.series.some(s => s.high_seed.team_id > 0);
				if (isCurrentSeason && hasActiveSeries) {
					allSeries = bracket.series;
					seasonLabel = bracket.season;
					isProjected = false;
					loading = false;
					return;
				}
			} catch { /* fall through */ }

			isProjected = true;
			const [standings, playIn] = await Promise.all([
				getStandings(),
				getPlayIn().catch(() => [] as PlayInGame[]),
			]);
			buildProjectedBracket(standings, playIn);
			const now = new Date();
			const startYear = now.getMonth() >= 8 ? now.getFullYear() : now.getFullYear() - 1;
			seasonLabel = `${startYear}-${String(startYear + 1).slice(-2)}`;
		} catch (e: any) {
			error = e.message || 'Failed to load bracket data';
		}
		loading = false;
	});

	function getSeriesByRoundConf(round: number, conference: string): BracketSeries[] {
		return allSeries
			.filter(s => s.round === round && s.conference === conference)
			.sort((a, b) => a.display_order - b.display_order);
	}

	function getFinals(): BracketSeries | null {
		const finals = allSeries.filter(s => s.round === 4);
		return finals.length > 0 ? finals[0] : null;
	}

	function isWinner(series: BracketSeries, seed: 'high' | 'low'): boolean {
		if (!series.series_winner) return false;
		const team = seed === 'high' ? series.high_seed : series.low_seed;
		return series.series_winner === team.team_id;
	}

	function isLoser(series: BracketSeries, seed: 'high' | 'low'): boolean {
		if (!series.series_winner) return false;
		return !isWinner(series, seed);
	}

	function hasTeams(series: BracketSeries): boolean {
		return series.high_seed.team_id !== 0 && series.low_seed.team_id !== 0;
	}

	function getVenue(series: BracketSeries): string {
		if (!hasTeams(series)) return '';
		return arenas[series.high_seed.city] || series.high_seed.city;
	}

	$: finals = getFinals();
</script>

<div class="playoffs-page">
	{#if loading}
		<h1>Playoffs</h1>
		<Skeleton width="100%" height="600px" />
	{:else if error}
		<h1>Playoffs</h1>
		<div class="error">{error}</div>
	{:else}
		<h1>{isProjected ? 'Projected Playoff Bracket' : 'Playoffs'} {seasonLabel}</h1>
		{#if isProjected}
			<p class="subtitle">Based on current standings. Updates as the season progresses.</p>
		{/if}

		<div class="bracket-container">
			<div class="conf-label east-label">Eastern Conference</div>
			<div class="conf-label west-label">Western Conference</div>

			<!-- Finals: spans center two columns above conf finals -->
			<div class="finals">
				<div class="finals-label">NBA Finals</div>
				{#if finals && hasTeams(finals)}
					<div class="matchup finals-matchup" in:fly={{ y: -20, duration: 400, delay: 600 }}>
						<div class="team-row" class:winner={isWinner(finals, 'high')} class:loser={isLoser(finals, 'high')} style="--team-color: {getTeamColor(finals.high_seed.tricode)}">
							<span class="seed">{finals.high_seed.rank}</span>
							<span class="team-name">{finals.high_seed.name}</span>
							<span class="series-wins">{finals.high_seed.wins}</span>
						</div>
						<div class="team-row" class:winner={isWinner(finals, 'low')} class:loser={isLoser(finals, 'low')} style="--team-color: {getTeamColor(finals.low_seed.tricode)}">
							<span class="seed">{finals.low_seed.rank}</span>
							<span class="team-name">{finals.low_seed.name}</span>
							<span class="series-wins">{finals.low_seed.wins}</span>
						</div>
						{#if finals.series_text}
							<div class="series-status">{finals.series_text}</div>
						{/if}
						<div class="venue">{getVenue(finals)}</div>
					</div>
				{:else}
					<div class="matchup finals-matchup">
						<div class="team-row tbd"><span class="team-name">East Champion</span></div>
						<div class="team-row tbd"><span class="team-name">West Champion</span></div>
					</div>
				{/if}
			</div>

			<!-- East: R1 → R2 → CF -->
			{#each [1, 2, 3] as round}
					<div class="round round-{round} east-round">
						{#each getSeriesByRoundConf(round, 'East') as series, i}
							<div class="matchup" in:fly={{ x: -20, duration: 300, delay: i * 100 + round * 150 }}>
								{#if hasTeams(series)}
									<div class="team-row" class:winner={isWinner(series, 'high')} class:loser={isLoser(series, 'high')} style="--team-color: {getTeamColor(series.high_seed.tricode)}">
										<span class="seed">{series.high_seed.rank}</span>
										<span class="team-name">{series.high_seed.name}</span>
										{#if isProjected}
											<span class="team-record">{series.high_seed.team_id > 0 ? `${series.high_seed.reg_wins}-${series.high_seed.reg_losses}` : ''}</span>
										{:else}
											<span class="series-wins">{series.high_seed.wins}</span>
										{/if}
									</div>
									<div class="team-row" class:winner={isWinner(series, 'low')} class:loser={isLoser(series, 'low')} style="--team-color: {getTeamColor(series.low_seed.tricode)}">
										<span class="seed">{series.low_seed.rank}</span>
										<span class="team-name">{series.low_seed.name}</span>
										{#if isProjected}
											<span class="team-record">{series.low_seed.team_id > 0 ? `${series.low_seed.reg_wins}-${series.low_seed.reg_losses}` : ''}</span>
										{:else}
											<span class="series-wins">{series.low_seed.wins}</span>
										{/if}
									</div>
									<div class="venue">{getVenue(series)}</div>
								{:else}
									<div class="team-row tbd"><span class="team-name">TBD</span></div>
									<div class="team-row tbd"><span class="team-name">TBD</span></div>
								{/if}
							</div>
						{/each}
					</div>
				{/each}

				<!-- West: CF ← R2 ← R1 (mirrored) -->
				{#each [3, 2, 1] as round}
					<div class="round round-{round} west-round">
						{#each getSeriesByRoundConf(round, 'West') as series, i}
							<div class="matchup" in:fly={{ x: 20, duration: 300, delay: i * 100 + (4 - round) * 150 }}>
								{#if hasTeams(series)}
									<div class="team-row" class:winner={isWinner(series, 'high')} class:loser={isLoser(series, 'high')} style="--team-color: {getTeamColor(series.high_seed.tricode)}">
										{#if isProjected}
											<span class="team-record">{series.high_seed.team_id > 0 ? `${series.high_seed.reg_wins}-${series.high_seed.reg_losses}` : ''}</span>
										{:else}
											<span class="series-wins">{series.high_seed.wins}</span>
										{/if}
										<span class="team-name right">{series.high_seed.name}</span>
										<span class="seed">{series.high_seed.rank}</span>
									</div>
									<div class="team-row" class:winner={isWinner(series, 'low')} class:loser={isLoser(series, 'low')} style="--team-color: {getTeamColor(series.low_seed.tricode)}">
										{#if isProjected}
											<span class="team-record">{series.low_seed.team_id > 0 ? `${series.low_seed.reg_wins}-${series.low_seed.reg_losses}` : ''}</span>
										{:else}
											<span class="series-wins">{series.low_seed.wins}</span>
										{/if}
										<span class="team-name right">{series.low_seed.name}</span>
										<span class="seed">{series.low_seed.rank}</span>
									</div>
									<div class="venue">{getVenue(series)}</div>
								{:else}
									<div class="team-row tbd"><span class="team-name">TBD</span></div>
									<div class="team-row tbd"><span class="team-name">TBD</span></div>
								{/if}
							</div>
						{/each}
					</div>
				{/each}
		</div>

		<!-- Play-In section -->
		{#if isProjected && (eastResult || westResult)}
			<div class="playin-container">
				<h2>Play-In Tournament</h2>
				<div class="playin-grid">
					{#each [{ label: 'Eastern', r: eastResult }, { label: 'Western', r: westResult }] as col}
						{#if col.r}
							<div class="playin-conf">
								<div class="playin-conf-title">{col.label}</div>
								{#each col.r.games as g, i (g.game_id)}
									{@const homeWon = g.status === 3 && g.home_score > g.away_score}
									{@const awayWon = g.status === 3 && g.away_score > g.home_score}
									<div class="playin-game" in:fly={{ y: 8, duration: 200, delay: i * 60 + 500 }}>
										<div class="playin-game-label">{g.label}</div>
										<div class="playin-row" class:winner={awayWon} class:loser={homeWon && !awayWon} style="--team-color: {getTeamColor(g.away_tricode)}">
											<span class="playin-seed">#{g.away_seed}</span>
											<span class="playin-tc">{g.away_tricode}</span>
											<span class="playin-team-name">{g.away_name}</span>
											<span class="playin-score">{g.status === 3 ? g.away_score : ''}</span>
										</div>
										<div class="playin-row" class:winner={homeWon} class:loser={awayWon} style="--team-color: {getTeamColor(g.home_tricode)}">
											<span class="playin-seed">#{g.home_seed}</span>
											<span class="playin-tc">{g.home_tricode}</span>
											<span class="playin-team-name">{g.home_name}</span>
											<span class="playin-score">{g.status === 3 ? g.home_score : ''}</span>
										</div>
										<div class="playin-game-status">{g.status_text}</div>
									</div>
								{/each}
							</div>
						{/if}
					{/each}
				</div>
			</div>
		{/if}
	{/if}
</div>

<style>
	.playoffs-page {
		margin: 0 auto;
	}

	h1 {
		font-size: 2rem;
		margin-bottom: 0.5rem;
		text-align: center;
		background: linear-gradient(135deg, var(--text-primary), var(--accent-orange));
		-webkit-background-clip: text;
		-webkit-text-fill-color: transparent;
		background-clip: text;
	}

	.subtitle {
		text-align: center;
		color: var(--text-muted);
		font-size: 0.9rem;
		margin-bottom: 2rem;
	}

	/* 6-column, 3-row grid:
	   Row 1: conference labels
	   Row 2: Finals spanning center two columns (above CF rounds)
	   Row 3: all rounds */
	.bracket-container {
		display: grid;
		grid-template-columns: minmax(170px, 1fr) minmax(170px, 1fr) minmax(170px, 1fr) minmax(170px, 1fr) minmax(170px, 1fr) minmax(170px, 1fr);
		grid-template-rows: auto auto 1fr;
		gap: 0.5rem 0.5rem;
		row-gap: 0;
		align-items: start;
	}

	.conf-label {
		font-family: var(--font-heading);
		font-size: 0.85rem;
		font-weight: 700;
		color: var(--text-secondary);
		text-transform: uppercase;
		letter-spacing: 0.1em;
		text-align: center;
		padding-bottom: 0.5rem;
	}

	.east-label { grid-column: 1 / 4; grid-row: 1; text-align: left; }
	.west-label { grid-column: 4 / 7; grid-row: 1; text-align: right; }

	.finals {
		grid-column: 3 / 5;
		grid-row: 2;
		display: flex;
		flex-direction: column;
		align-items: center;
		align-self: end;
		gap: 0.5rem;
		padding-bottom: 0;
		margin-bottom: 0;
	}

	.finals-label {
		font-family: var(--font-heading);
		font-size: 1rem;
		font-weight: 700;
		color: var(--accent-orange);
		text-transform: uppercase;
		letter-spacing: 0.1em;
	}

	.round {
		display: flex;
		flex-direction: column;
		justify-content: space-around;
		min-height: 480px;
		gap: 0.5rem;
		grid-row: 3;
	}

	.east-round.round-1 { grid-column: 1; }
	.east-round.round-2 { grid-column: 2; }
	.east-round.round-3 { grid-column: 3; }

	.west-round.round-3 { grid-column: 4; }
	.west-round.round-2 { grid-column: 5; }
	.west-round.round-1 { grid-column: 6; }

	.matchup {
		background: var(--bg-card);
		border: 1px solid var(--border-subtle);
		border-radius: var(--radius-sm);
		overflow: hidden;
	}

	.finals-matchup {
		min-width: 280px;
	}

	.finals-matchup .team-name {
		font-size: 1rem;
	}

	.finals-matchup .series-wins {
		font-size: 1.3rem;
	}

	.team-row {
		display: flex;
		align-items: center;
		gap: 0.35rem;
		padding: 0.5rem 0.5rem;
		border-left: 3px solid var(--team-color, var(--border-subtle));
		transition: all 0.2s ease;
	}

	.west-round .team-row {
		border-left: none;
		border-right: 3px solid var(--team-color, var(--border-subtle));
	}

	.team-row + .team-row {
		border-top: 1px solid var(--border-subtle);
	}

	.team-row.winner {
		background: rgba(255, 255, 255, 0.05);
	}

	.team-row.winner .team-name {
		color: #ffffff;
		font-weight: 700;
	}

	.team-row.winner .series-wins {
		color: var(--accent-green);
		font-weight: 700;
	}

	.team-row.loser {
		opacity: 0.4;
	}

	.team-row.tbd {
		border-left-color: var(--border-subtle);
		border-right-color: var(--border-subtle);
	}

	.seed {
		font-size: 0.7rem;
		font-weight: 700;
		color: var(--text-muted);
		min-width: 1rem;
		text-align: center;
		flex-shrink: 0;
	}

	.team-name {
		font-family: var(--font-heading);
		font-size: 0.8rem;
		font-weight: 600;
		flex: 1;
		min-width: 0;
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
	}

	.team-name.right {
		text-align: right;
	}

	.tbd .team-name {
		color: var(--text-muted);
		font-style: italic;
	}

	.team-record {
		font-size: 0.7rem;
		color: var(--text-muted);
		font-variant-numeric: tabular-nums;
		white-space: nowrap;
		flex-shrink: 0;
	}

	.series-wins {
		font-family: var(--font-heading);
		font-size: 1rem;
		font-weight: 700;
		min-width: 1.2rem;
		text-align: center;
	}

	.series-status {
		font-size: 0.65rem;
		color: var(--text-muted);
		text-align: center;
		padding: 0.3rem 0.5rem;
		border-top: 1px solid var(--border-subtle);
		background: rgba(0, 0, 0, 0.2);
	}

	.venue {
		font-size: 0.6rem;
		color: var(--text-muted);
		text-align: center;
		padding: 0.3rem 0.5rem;
		border-top: 1px solid var(--border-subtle);
		opacity: 0.7;
	}

	/* Play-In section */
	.playin-container {
		margin-top: 2.5rem;
		padding-top: 1.5rem;
		border-top: 1px dashed var(--border-subtle);
	}

	.playin-container h2 {
		text-align: center;
		font-size: 1.1rem;
		color: var(--text-secondary);
		margin-bottom: 1rem;
	}

	.playin-grid {
		display: grid;
		grid-template-columns: 1fr 1fr;
		gap: 3rem;
		max-width: 700px;
		margin: 0 auto;
	}

	.playin-conf-title {
		font-size: 0.75rem;
		font-weight: 700;
		text-transform: uppercase;
		letter-spacing: 0.08em;
		color: var(--text-muted);
		margin-bottom: 0.5rem;
		padding-bottom: 0.35rem;
		border-bottom: 1px solid var(--border-subtle);
	}

	.playin-game {
		margin-bottom: 0.85rem;
		padding: 0.5rem 0.65rem;
		background: var(--bg-card);
		border: 1px solid var(--border-subtle);
		border-radius: var(--radius-sm);
	}

	.playin-game-label {
		font-size: 0.7rem;
		font-weight: 600;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		color: var(--text-muted);
		margin-bottom: 0.35rem;
	}

	.playin-row {
		display: flex;
		align-items: center;
		gap: 0.6rem;
		padding: 0.3rem 0 0.3rem 0.65rem;
		margin: 0.2rem 0;
		font-size: 0.9rem;
		border-left: 3px solid var(--team-color, var(--border-subtle));
	}

	.playin-seed {
		width: 2rem;
		font-size: 0.75rem;
		font-weight: 700;
		color: var(--text-muted);
		font-variant-numeric: tabular-nums;
	}

	.playin-tc {
		width: 2.8rem;
		font-weight: 700;
		color: var(--text-secondary);
		font-variant-numeric: tabular-nums;
	}

	.playin-team-name {
		flex: 1;
		font-family: var(--font-heading);
		font-weight: 600;
	}

	.playin-score {
		width: 2.5rem;
		text-align: right;
		font-variant-numeric: tabular-nums;
		font-weight: 600;
	}

	.playin-row.winner { color: var(--accent-green); }
	.playin-row.loser { color: var(--text-muted); opacity: 0.6; }

	.playin-game-status {
		margin-top: 0.25rem;
		font-size: 0.7rem;
		color: var(--text-muted);
		text-align: right;
	}

	.error {
		text-align: center;
		padding: 3rem;
		color: var(--accent-red);
	}
</style>
