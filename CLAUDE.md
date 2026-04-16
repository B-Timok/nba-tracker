# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

All Python commands assume the venv is active or invoke `.venv/bin/python` / `.venv/bin/pytest` explicitly (the `web/run.py` dev runner hard-codes `.venv/bin/python`).

**Setup** (first time only):
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -r web/backend/requirements.txt   # adds uvicorn
cd web/frontend && npm install && cd ../..
```

**Run dev stack** (FastAPI on :8000 + Vite on :5173, proxies `/api` to backend):
```bash
.venv/bin/python web/run.py
```

**Run TUI / legacy CLI:**
```bash
.venv/bin/python -m cli        # Textual TUI
python CLI_Scores.py           # legacy one-shot script
```

**Tests** — `pytest.ini` excludes the `integration` marker by default:
```bash
.venv/bin/pytest tests/ -v                              # unit + API tests (no network)
.venv/bin/pytest tests/test_integration.py -v -m integration   # hits the real NBA CDN
.venv/bin/pytest tests/test_api.py::test_standings_endpoint -v # single test
```

Note: `tests/test_api.py` uses FastAPI's `TestClient` against `web.backend.main:app`, which calls the real NBA API through the shared `client = NBAClient()` module-level singleton in `web/backend/routers/api.py`. These are effectively live network tests despite not being marked `integration`.

**Frontend type-check:**
```bash
cd web/frontend && npm run check
```

**Frontend production build** (SvelteKit uses `adapter-static` → outputs to `web/frontend/build/`; `web/backend/main.py` auto-mounts it at `/` if present):
```bash
cd web/frontend && npm run build
```

## Architecture

Three UIs share a single Python data layer. Understanding that layering is the key to making changes safely.

### Shared data layer: `nba_api/`

- `endpoints.py` — URL builders only. Two upstream hosts: `cdn.nba.com` (free, no headers) and `stats.nba.com` (requires browser-like `User-Agent` / `Referer` — see `NBAEndpoints.stats_headers()`).
- `client.py` — `NBAClient` wraps a `requests.Session` with those stats headers pre-applied and an in-process TTL cache (`_Cache`). Two important conventions:
  - **Dual scoreboard paths.** `get_scoreboard()` hits `stats.nba.com/scoreboardv3` (or the live CDN for today). `get_scoreboard_cdn()` instead pulls the full-season `scheduleLeagueV2_1.json` from the static CDN and filters it client-side. The FastAPI scoreboard route uses the CDN variant; TUI/tests generally use `get_scoreboard()`. The two return the same `Game` shape but from different upstream data.
  - **Standings fallback.** `get_standings()` hits stats.nba.com. `get_standings_cdn()` reconstructs standings by walking completed games in the cached schedule and applying a hardcoded tricode→conference/division map. Teams not in that map (exhibition, All-Star, international) are intentionally filtered out.
  - Live scoreboard entries are only cached when no game is live and at least one is final; everything else caches for `CACHE_LONG` (1 hour).
- `models.py` — dataclasses consumed by all three UIs and serialized (manually, field by field) by the FastAPI router. Adding a field here means updating the serialization helpers in `web/backend/routers/api.py` **and** the matching TypeScript type in `web/frontend/src/lib/types.ts`.
- `date_utils.py` — `game_date_to_season()` rolls over in **September** (month ≥ 9 counts as the new season), not October, because preseason starts in late September.

### Web: `web/`

- **Backend** (`web/backend/main.py` + `routers/api.py`). FastAPI app with a single `APIRouter` under `/api`. `main.py` inserts the repo root into `sys.path` so `nba_api` imports work when uvicorn is launched from anywhere. It also mounts the SvelteKit `build/` directory at `/` when present, so the same FastAPI app serves the frontend in production.
- The router holds a **module-level `NBAClient` singleton** (`client = NBAClient()`). Its cache persists for the life of the uvicorn process — reloads via `--reload` wipe it.
- Two endpoints (`/api/player/{id}` and `/api/playoffs`) bypass `NBAClient`'s parsers and hit `stats.nba.com` / the CDN bracket JSON directly, reusing `client._session` for the preset headers. The playoff endpoint walks backwards up to 3 years to find a published bracket.
- **Frontend** (`web/frontend/`). SvelteKit 2 + Svelte 5 + TypeScript, `adapter-static` (SPA-style with `fallback: 'index.html'`). Vite dev server proxies `/api` → `http://localhost:8000` (see `vite.config.ts`) — all fetches in `src/lib/api.ts` use the relative `/api` prefix so dev and prod behave identically.
- Shared state lives in `src/lib/stores.ts` (`currentDate` custom store with `next/prev/today` helpers, `selectedGame`). Team colors for all 30 tricodes live in `src/lib/teamColors.ts` and are the canonical color source for the whole UI — don't hardcode team colors elsewhere.

### Terminal UI: `cli/`

Textual app. `app.py` installs three screens (`ScoreboardScreen`, `StandingsScreen`, `StatsScreen`) up front and `_switch_to()` pops the stack back to the base before pushing a new top-level screen — this is how the `1`/`2`/`3` hotkeys avoid stacking. Detail screens (`boxscore`, `playbyplay`) are pushed on top of the scoreboard. Each screen constructs its own calls against the shared `NBAClient` passed from `NBAApp`.

### Legacy: `CLI_Scores.py`

Standalone script that predates `nba_api/`. Hits the today's-scoreboard CDN URL directly with its own `requests.get`. Left as-is; new work should go through `nba_api`.

## Conventions worth knowing

- **No API keys anywhere** — both upstream hosts are public. Don't add auth headers beyond what `NBAEndpoints.stats_headers()` returns (stats.nba.com 403s without the browser-like UA/Referer).
- **Season format** is always `"YYYY-YY"` (e.g. `"2025-26"`). Use `game_date_to_season()`; don't build it inline.
- **Game status codes** are `1=scheduled, 2=live, 3=final` and show up both as raw ints (models) and as `is_scheduled/is_live/is_final` booleans (API JSON).
- **When adding a new API field**: update `models.py` → serialization helper in `routers/api.py` → `types.ts` → consuming Svelte component. Skipping the types file produces silent `undefined` reads at runtime because `svelte-check` isn't in the dev-run loop.
- **Date fixtures** in `tests/fixtures/` are from the 2025-26 season (game `0022501186`, dates around 2026-04-12). Integration and TestClient tests reference these specific IDs/dates — if you regenerate fixtures, update the assertions in `test_api.py` and `test_integration.py` together.
