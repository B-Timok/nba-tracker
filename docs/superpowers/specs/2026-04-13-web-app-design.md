# NBA Web App — Design Spec

## Overview

A bold, playful web application for browsing NBA scores, box scores, play-by-play, standings, and stats. Built with SvelteKit frontend + FastAPI backend, served as a monolith. Reuses the existing `nba_api` data layer.

Future phases (not in this spec): player profiles, team pages, win predictions, playoff brackets.

## Tech Stack

- **Frontend:** SvelteKit, TypeScript, Vite
- **Backend:** FastAPI, uvicorn
- **Data:** `nba_api` package (already built)
- **Fonts:** Bold/playful selection (e.g., Space Grotesk for headings, Inter for body)
- **No database** — all data from NBA API via `nba_api.NBAClient`

## Architecture

```
web/
├── backend/
│   ├── main.py           # FastAPI app, serves API + static files
│   ├── routers/
│   │   └── api.py        # /api/* endpoints wrapping nba_api
│   └── requirements.txt  # fastapi, uvicorn
├── frontend/
│   ├── src/
│   │   ├── routes/       # SvelteKit file-based routing
│   │   ├── lib/
│   │   │   ├── components/   # Reusable Svelte components
│   │   │   ├── stores/       # Svelte stores (shared state)
│   │   │   └── api.ts        # Fetch wrappers for /api/*
│   │   └── app.html
│   ├── static/
│   ├── package.json
│   ├── svelte.config.js
│   └── vite.config.ts
└── run.py                # Dev runner: starts FastAPI + Vite
```

**Data flow:** SvelteKit pages → `lib/api.ts` → FastAPI `/api/*` → `nba_api.NBAClient` → NBA CDN/stats.nba.com

**Dev workflow:** `python run.py` starts both servers. Vite proxies `/api/*` to FastAPI. Hot reload on frontend changes.

**Production:** `npm run build` compiles Svelte to static files. FastAPI serves them + the API.

## API Endpoints

| Endpoint | Method | Params | Returns |
|----------|--------|--------|---------|
| `/api/scoreboard/{date}` | GET | date (YYYY-MM-DD) | List of games |
| `/api/game/{game_id}/boxscore` | GET | game_id | Home + away box scores |
| `/api/game/{game_id}/playbyplay` | GET | game_id | List of play actions |
| `/api/standings` | GET | season (query param) | List of standings entries |
| `/api/stats/players` | GET | season (query param) | List of player stats |
| `/api/stats/teams` | GET | season (query param) | List of team stats |

All endpoints return JSON. Errors return `{"error": "message"}` with appropriate HTTP status.

## Pages

### Scoreboard (`/`)

- Default landing page showing all games for today
- Date navigation: left/right arrows + clickable date picker
- Game cards in a grid layout:
  - Team names with city, record
  - Score (large, bold typography)
  - Game status: scheduled (blue), live (green pulsing), final (gray)
  - Game leader summary
- Clicking a card navigates to `/game/[id]`
- Auto-refresh every 15 seconds when live games exist
- Loading skeletons while data loads

### Game Detail (`/game/[id]`)

- Score header: both teams, score, status (large and prominent)
- Tabbed content: Box Score | Play-by-Play
- **Box Score tab:** Two tables (home/away) with full player stats, starters/bench split, team totals. Sortable columns on click.
- **Play-by-Play tab:** Scrollable feed with period separators, timestamps, running score. Auto-scrolls on live games.
- Back link to scoreboard

### Standings (`/standings`)

- Two tabs: Eastern Conference | Western Conference
- Table: rank, team, W, L, PCT, GB, home, road, L10, streak
- Sortable columns
- Hover highlight on rows
- Clinch indicators displayed

### Stats (`/stats`)

- Two tabs: Player Stats | Team Stats
- Search/filter bar at top (live filtering as you type)
- Sortable table with season averages
- Player table: name, team, GP, MPG, PPG, RPG, APG, SPG, BPG, FG%, 3P%, FT%, +/-
- Team table: name, GP, W, L, PPG, RPG, APG, SPG, BPG, FG%, 3P%, FT%, +/-
- Default sort: PPG descending

## Visual Design

**Vibe:** Bold and playful — bright accent colors, big typography, personality.

**Color palette:**
- Background: dark (#0a0a0f) with subtle gradient
- Cards: slightly lighter (#14141f) with colored borders/accents
- Primary accent: electric blue (#3b82f6)
- Secondary accent: hot orange (#f97316)
- Live indicator: green (#22c55e)
- Final: muted gray (#6b7280)
- Scheduled: sky blue (#38bdf8)
- Text: white (#f8fafc) with muted secondary (#94a3b8)

**Typography:**
- Headings: Space Grotesk (bold, geometric, playful)
- Body/data: Inter (clean, great for numbers and tables)
- Scores: Space Grotesk at large sizes with variable weight

**Animations & Interactivity:**
- Smooth page transitions (SvelteKit built-in transitions, crossfade between routes)
- Loading skeletons with shimmer effect
- Live score ticker with animated number changes (flip/roll animation)
- Game cards: lift on hover (subtle translateY + shadow), border glow on live games
- Stats tables: row highlight on hover, smooth sort transitions
- Micro-interactions: buttons scale on press, tabs slide indicator
- Score updates pulse briefly when values change

## Navigation

- Persistent top nav bar: logo/title, Scores, Standings, Stats links
- Active page indicator (underline/highlight)
- Date picker integrated in nav (visible on all pages, drives scoreboard)
- Mobile-responsive: hamburger menu on small screens

## Error Handling

- Network errors: show inline error message with retry button
- No games: "No games scheduled" centered message
- Loading states: skeleton placeholders on every data-dependent view
- API timeout: 5 second limit, show error with retry

## Live Features

- Auto-refresh every 15 seconds when viewing a date with live games
- Visual indicator in nav bar when live games are active
- Score change animation (number rolls/flips when score updates)
- No polling on historical dates or days with all finals
