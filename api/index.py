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
    root = str(Path(__file__).resolve().parent.parent)
    cwd = os.getcwd()
    files_at_root = os.listdir(root) if os.path.isdir(root) else "NOT A DIR"
    files_at_cwd = os.listdir(cwd)
    nba_api_exists = os.path.isdir(os.path.join(root, "nba_api"))
    web_exists = os.path.isdir(os.path.join(root, "web"))

    # Try importing
    import_error = None
    try:
        if root not in sys.path:
            sys.path.insert(0, root)
        from web.backend.routers.api import router
    except Exception as e:
        import_error = str(e)

    return {
        "status": "ok",
        "root": root,
        "cwd": cwd,
        "files_at_root": files_at_root,
        "files_at_cwd": files_at_cwd,
        "nba_api_exists": nba_api_exists,
        "web_exists": web_exists,
        "sys_path": sys.path[:5],
        "import_error": import_error,
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
