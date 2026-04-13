# NBA Live Scoreboard

<img width="1250" height="733" alt="image" src="https://github.com/user-attachments/assets/f0f31986-a91a-402f-af50-9495269ab9b9" />


A full-stack application for browsing NBA scores, box scores, play-by-play, standings, player profiles, and playoff brackets. Features three interfaces: a web app (SvelteKit + FastAPI), an interactive terminal UI (Textual), and a simple CLI.

## Features

- **Scoreboard** — View all games for any date with scores, status, and game leaders
- **Box Score** — Full player stats (points, rebounds, assists, shooting splits, +/-) with starters/bench split
- **Play-by-Play** — Scrollable feed of every play, grouped by quarter
- **Standings** — Eastern and Western conference standings with W/L, PCT, GB, streak, L10
- **Player/Team Stats** — Season averages with category filters (Points, Rebounds, Assists, etc.), search, pagination
- **Player Profiles** — Bio, headline stats, and full career stats with season-by-season breakdown
- **Playoff Bracket** — Projected bracket from current standings with venue info, switches to live bracket during playoffs
- **Team Colors** — All 30 NBA teams with accurate primary colors throughout the UI
- **Date Navigation** — Browse any date in NBA history
- **Live Updates** — Auto-refreshes every 15 seconds when live games are in progress

## Prerequisites

- Python 3.12+
- Node.js 18+ (for web app)
- pip or uv

## Setup

```bash
cd sportsScores

# Create virtual environment and install dependencies
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install fastapi "uvicorn[standard]"

# Install frontend dependencies
cd web/frontend
npm install
cd ../..
```

## Usage

### Web App (recommended)

The web app runs a FastAPI backend serving the NBA API and a SvelteKit frontend with a dark-themed, interactive UI.

```bash
.venv/bin/python web/run.py
```

This starts both servers — FastAPI on port 8000 and Vite dev server on port 5173 (auto-opens in browser).

**Pages:**

| Page | URL | Description |
|------|-----|-------------|
| Scores | `/` | Game cards for any date, date navigation, auto-refresh for live games |
| Game Detail | `/game/[id]` | Box score + play-by-play with tabbed view |
| Standings | `/standings` | East/West conference tabs with playoff/play-in lines |
| Stats | `/stats` | Player and team stats with category filters and search |
| Player Profile | `/player/[id]` | Bio, headline stats, career stats table |
| Playoffs | `/playoffs` | Projected bracket from standings, live bracket during playoffs |

### Interactive TUI

A terminal-based UI built with Textual.

```bash
.venv/bin/python -m cli
```

**Keyboard Controls:**

| Key | Action |
|-----|--------|
| `1` | Scoreboard |
| `2` | Standings |
| `3` | Stats |
| Left/Right | Change date |
| `d` | Go to specific date |
| Enter | Open game detail (box score) |
| `p` | Play-by-play (from box score) |
| `/` or `s` | Search (in stats view) |
| Escape | Go back |
| `r` | Refresh |
| `q` | Quit |

### Legacy CLI

Simple terminal output of today's scores.

```bash
python CLI_Scores.py
```

## Project Structure

```
sportsScores/
├── nba_api/                  # Shared data layer
│   ├── models.py             # Dataclasses (Game, BoxScore, Standings, etc.)
│   ├── client.py             # API client with caching
│   ├── endpoints.py          # NBA API URL construction
│   └── date_utils.py         # Date parsing and season calculation
├── web/                      # Web application
│   ├── backend/
│   │   ├── main.py           # FastAPI app
│   │   └── routers/api.py    # All REST API endpoints
│   ├── frontend/             # SvelteKit app
│   │   └── src/
│   │       ├── routes/       # Pages (scores, game detail, standings, stats, playoffs, player)
│   │       └── lib/
│   │           ├── components/   # Svelte components (GameCard, BoxScore, Nav, etc.)
│   │           ├── teamColors.ts # NBA team color mapping
│   │           ├── api.ts        # API client
│   │           └── stores.ts     # Shared state (date, selected game)
│   └── run.py                # Dev runner (starts both servers)
├── cli/                      # Interactive TUI (Textual)
│   ├── app.py                # Main app
│   ├── screens/              # Scoreboard, BoxScore, PlayByPlay, Standings, Stats
│   └── widgets/              # DateBar, StatusBar
├── tests/                    # Unit and integration tests
├── CLI_Scores.py             # Legacy simple CLI
└── requirements.txt
```

## Tech Stack

- **Data Layer:** Python, requests, pytz
- **Web Backend:** FastAPI, uvicorn
- **Web Frontend:** SvelteKit, TypeScript, Vite
- **Terminal UI:** Textual
- **Data Source:** NBA CDN (cdn.nba.com) — no API keys required

## Tests

```bash
# Unit tests
.venv/bin/pytest tests/ -v

# Live integration tests (hits real NBA API)
.venv/bin/pytest tests/test_integration.py -v -m integration

# API endpoint tests
.venv/bin/pytest tests/test_api.py -v
```
