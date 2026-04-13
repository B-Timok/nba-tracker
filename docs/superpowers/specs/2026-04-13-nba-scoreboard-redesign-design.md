# NBA Live Scoreboard — Redesign Spec

## Overview

Redesign the existing NBA scoreboard project from simple single-file scripts into a layered application with a shared data layer, an interactive CLI (TUI), and a PySide6 desktop GUI. Scope is NBA only for now, with full historical date support and deep stat coverage.

Future phases (not in this spec): multi-sport support (NFL, MLB, NHL) and a web application.

## Data Layer (`nba_api`)

The shared foundation consumed by both CLI and GUI.

### API Client (`client.py`)

- Wraps NBA CDN endpoints for: scoreboard, box scores, play-by-play, standings, player/team stats.
- Supports any historical date via date-parameterized endpoints.
- Returns clean Python dataclasses — no raw JSON leaks into presentation layers.
- 10-15 second polling for live game data with a callback/event system so UI layers can subscribe to updates.
- 5-second request timeout. Graceful handling when offline or CDN is down.

### Data Models (`models.py`)

- `Game` — teams, scores, status (scheduled/live/final/postponed), game time, leaders, overtime info.
- `BoxScore` — full player stats for a game (points, rebounds, assists, steals, blocks, FG%, etc.), team totals.
- `PlayByPlay` — individual plays with timestamps, quarter/period separators, running score.
- `Standings` — conference/division rankings, W/L, PCT, GB, streak, L10.
- `PlayerStats` / `TeamStats` — season averages.

### Caching

- In-memory cache for the current session to avoid redundant API calls when switching views.
- Completed/final games cached longer (data won't change).
- Live games bypass cache on each refresh cycle.
- When offline, show last cached data with a "no connection" indicator.

### Date Navigation (`date_utils.py`)

- Resolves "today", "yesterday", relative dates, and arbitrary `YYYY-MM-DD` input.
- Validates date input before making API calls.
- Knows NBA schedule boundaries (season start/end, all-star break) for smarter navigation.

### Endpoints (`endpoints.py`)

- URL construction for each NBA CDN endpoint.
- All endpoints are public, no API keys needed.

## CLI — Interactive TUI (Textual)

### Views

- **Scoreboard** (default) — all games for the selected date in a table: teams, scores, status, game time. Live games highlighted with a visual indicator.
- **Box Score** — drill into a game for full player stats in a sortable table per team, with team totals.
- **Play-by-Play** — scrollable feed of plays for a selected game. Auto-scrolls during live games.
- **Standings** — conference and division standings with W/L, PCT, GB, streak, L10.
- **Player/Team Stats** — season averages, searchable and sortable.

### Navigation & Controls

- Left/right arrow keys — change dates.
- Tab or number keys — switch between views (Scoreboard / Standings / Stats).
- Enter on a game — open detail view (box score, play-by-play).
- Escape — go back.
- `/` or `s` — search (players, teams).
- `d` — type in a specific date.
- `q` — quit.

### Live Features

- Auto-refreshes every 10-15 seconds when viewing a date with live games.
- Visual indicator for live games (pulsing dot or color highlight).
- Status bar at bottom showing last refresh time and connection status.
- No polling on historical dates or days with all finals.

### Entry Point

`python -m cli`

## GUI — PySide6 Desktop App

### Layout

- **Top bar** — date selector (left/right arrows + calendar date picker), sport label ("NBA"), refresh indicator.
- **Sidebar** — navigation between views: Scoreboard, Standings, Player Stats, Team Stats.
- **Main content area** — displays the selected view.

### Scoreboard View

- Card-style layout for each game: team names, score, quarter/status, game time.
- Color coding: green for live, gray for final, blue for scheduled.
- Click a game card to expand into a detail panel with box score and play-by-play tabs.

### Box Score View

- Two tables (home/away) with full player stats.
- Column headers sortable by click.
- Team totals row at bottom.

### Play-by-Play View

- Scrollable list with timestamp, description, and score at that point.
- Quarter/period separators.
- Auto-scrolls during live games.

### Standings View

- Tabbed: Eastern / Western conference.
- Table with rank, team, W, L, PCT, GB, streak, L10.
- Sortable columns.

### Player/Team Stats View

- Search bar at top to filter.
- Sortable table of season averages.
- Click a player/team for a detailed stat card.

### Live Features

- 10-15 second auto-refresh for live games.
- Status bar at bottom with last refresh timestamp.
- Subtle highlight flash on game cards when scores change.
- Pause polling when app is minimized/backgrounded.
- Only poll when viewing a date with active live games.

### Window

- Resizable, remembers window size/position between sessions.
- Dark theme default, with option to toggle light.

### Entry Point

`python -m gui`

## Project Structure

```
sportsScores/
├── nba_api/
│   ├── __init__.py
│   ├── client.py          # API fetching, polling, caching
│   ├── models.py          # Dataclasses (Game, BoxScore, etc.)
│   ├── endpoints.py       # URL construction for each NBA endpoint
│   └── date_utils.py      # Date parsing, navigation, season boundaries
├── cli/
│   ├── __init__.py
│   ├── app.py             # Textual app entry point
│   ├── screens/
│   │   ├── scoreboard.py  # Scoreboard view
│   │   ├── boxscore.py    # Box score detail view
│   │   ├── playbyplay.py  # Play-by-play view
│   │   ├── standings.py   # Standings view
│   │   └── stats.py       # Player/team stats view
│   └── widgets/
│       └── game_card.py   # Reusable game display widget
├── gui/
│   ├── __init__.py
│   ├── app.py             # PySide6 app entry point
│   ├── views/
│   │   ├── scoreboard.py
│   │   ├── boxscore.py
│   │   ├── playbyplay.py
│   │   ├── standings.py
│   │   └── stats.py
│   └── widgets/
│       ├── game_card.py
│       ├── date_nav.py    # Date navigation bar
│       └── stat_table.py  # Reusable sortable table
├── CLI_Scores.py          # Legacy simple quick-check
├── GUI_Scores.py          # Legacy
├── requirements.txt
└── README.md
```

## Dependencies

- `requests` — HTTP client (existing)
- `pytz` — timezone handling (existing)
- `textual` — TUI framework for CLI
- `PySide6` — GUI framework

No API keys required — all NBA CDN endpoints are public.

## Error Handling & Edge Cases

### Network

- Graceful offline handling — show last cached data with "no connection" indicator.
- 5-second timeout on API calls — show retry prompt instead of hanging.
- Clear error message in current view if NBA CDN is down or returns unexpected data.

### Data Edge Cases

- No games on a date — display "No games scheduled."
- Preseason / All-Star / Playoff / Play-in games — handle gracefully, show what's available.
- Missing leader stats (game not started, data not populated) — show dashes or "N/A."
- Overtime games — display OT/2OT/etc. in status.
- Postponed or cancelled games — show status as-is from the API.
- Very old dates — may have less detailed data (no play-by-play, limited box scores). Degrade gracefully.
- Invalid date input — validate and show error.

### Live Refresh

- Only poll when viewing a date with live games.
- In detail view (box score), refresh that specific game, not entire scoreboard.
- Pause polling when GUI app is minimized/backgrounded.
