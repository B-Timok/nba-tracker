import sys
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Ensure nba_api is importable from project root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from web.backend.routers.api import router as api_router

app = FastAPI(title="NBA Scoreboard API")
app.include_router(api_router)

# Serve SvelteKit build output (production)
build_dir = Path(__file__).resolve().parent.parent / "frontend" / "build"
if build_dir.exists():
    app.mount("/", StaticFiles(directory=str(build_dir), html=True), name="static")
