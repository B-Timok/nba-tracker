"""Vercel serverless function — wraps the FastAPI app."""
import sys
import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

# Debug endpoint — always works, no local imports needed
@app.get("/api/health")
def health():
    import requests as req
    import traceback

    # Test CDN endpoint (fast, should always work)
    cdn_result = None
    cdn_error = None
    try:
        r = req.get(
            "https://cdn.nba.com/static/json/liveData/scoreboard/todaysScoreboard_00.json",
            headers={"User-Agent": "Mozilla/5.0", "Referer": "https://www.nba.com/"},
            timeout=9,
        )
        cdn_result = {"status": r.status_code, "games": len(r.json().get("scoreboard", {}).get("games", []))}
    except Exception as e:
        cdn_error = traceback.format_exc()

    # Test stats.nba.com (slower)
    stats_result = None
    stats_error = None
    try:
        r = req.get(
            "https://stats.nba.com/stats/scoreboardv3?GameDate=2026-04-12&LeagueID=00",
            headers={"User-Agent": "Mozilla/5.0", "Referer": "https://www.nba.com/", "Accept": "application/json"},
            timeout=9,
        )
        stats_result = {"status": r.status_code, "games": len(r.json().get("scoreboard", {}).get("games", []))}
    except Exception as e:
        stats_error = traceback.format_exc()

    return {
        "cdn": cdn_result or cdn_error,
        "stats_nba": stats_result or stats_error,
    }

# Try to load the real API router
ROOT = str(Path(__file__).resolve().parent.parent)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

try:
    from web.backend.routers.api import router
    app.include_router(router)
except Exception as e:
    @app.get("/api/{path:path}")
    def fallback(path: str):
        return {"error": f"Failed to load API: {e}", "path": path}
