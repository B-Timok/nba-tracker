# NBA Live Scoreboard

A Python application for browsing NBA scores, box scores, play-by-play, standings, and player/team stats. Supports full historical date navigation using the NBA's public API.

## Features

- **Scoreboard** — View all games for any date with scores, status, and game leaders
- **Box Score** — Full player stats (points, rebounds, assists, shooting splits, +/-) with starters/bench split
- **Play-by-Play** — Scrollable feed of every play, grouped by quarter
- **Standings** — Eastern and Western conference standings with W/L, PCT, GB, streak, L10
- **Player/Team Stats** — Season averages sorted by PPG, with search/filter
- **Date Navigation** — Browse any date in NBA history
- **Live Updates** — Auto-refreshes every 15 seconds when live games are in progress

## Prerequisites

- Python 3.12+
- pip or uv

## Setup

```bash
# Clone and enter the project
cd sportsScores

# Create virtual environment and install dependencies
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

### Interactive TUI (recommended)

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

### Legacy CLI (simple output)

```bash
python CLI_Scores.py
```

## Project Structure

```
sportsScores/
├── nba_api/              # Shared data layer
│   ├── models.py         # Dataclasses (Game, BoxScore, Standings, etc.)
│   ├── client.py         # API client with caching
│   ├── endpoints.py      # NBA API URL construction
│   └── date_utils.py     # Date parsing and season calculation
├── cli/                  # Interactive TUI (Textual)
│   ├── app.py            # Main app entry point
│   ├── screens/          # Scoreboard, BoxScore, PlayByPlay, Standings, Stats
│   └── widgets/          # DateBar, StatusBar
├── tests/                # Unit and integration tests
├── CLI_Scores.py         # Legacy simple CLI
├── GUI_Scores.py         # Legacy tkinter GUI
└── requirements.txt
```

## Tests

```bash
# Unit tests
.venv/bin/pytest tests/ -v

# Live integration tests (hits real NBA API)
.venv/bin/pytest tests/test_integration.py -v -m integration
```
