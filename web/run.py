"""Dev runner: starts FastAPI backend + SvelteKit Vite dev server."""
import subprocess
import sys
import os
import signal
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = Path(__file__).resolve().parent / "backend"
FRONTEND_DIR = Path(__file__).resolve().parent / "frontend"
VENV_PYTHON = ROOT / ".venv" / "bin" / "python"


def main():
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT)

    # Start FastAPI
    api_proc = subprocess.Popen(
        [str(VENV_PYTHON), "-m", "uvicorn", "web.backend.main:app",
         "--reload", "--port", "8000"],
        cwd=str(ROOT),
        env=env,
    )

    # Start Vite dev server
    vite_proc = subprocess.Popen(
        ["npm", "run", "dev", "--", "--port", "5173", "--open"],
        cwd=str(FRONTEND_DIR),
    )

    def shutdown(sig, frame):
        api_proc.terminate()
        vite_proc.terminate()
        sys.exit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    try:
        api_proc.wait()
    except KeyboardInterrupt:
        shutdown(None, None)


if __name__ == "__main__":
    main()
