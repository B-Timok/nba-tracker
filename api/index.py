"""Vercel serverless function — wraps the FastAPI app."""
import sys
import os
from pathlib import Path

# Ensure project root is in Python path so nba_api and web.backend are importable
ROOT = str(Path(__file__).resolve().parent.parent)
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# Also try LAMBDA_TASK_ROOT for Vercel's runtime
task_root = os.environ.get("LAMBDA_TASK_ROOT", "")
if task_root and task_root not in sys.path:
    sys.path.insert(0, task_root)

from web.backend.routers.api import router
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(router)
