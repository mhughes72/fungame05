"""
FastAPI application entry point.

In production: serves the React SPA from web/dist/ and the game API at /api/.
In development: only serves the API (Vite dev server handles the frontend).
"""

import os

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from api.routes import router

app = FastAPI(title="Republic of Veridia — API")

# CORS (permissive for dev; tighten in production if needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API routes — must be registered before the static catch-all
app.include_router(router, prefix="/api")

# ── Serve React build ──────────────────────────────────────────────────────────
_HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_DIST = os.path.join(_HERE, "web", "dist")

if os.path.isdir(_DIST):
    # Vite puts JS/CSS/image bundles under web/dist/assets/
    _ASSETS = os.path.join(_DIST, "assets")
    if os.path.isdir(_ASSETS):
        app.mount("/assets", StaticFiles(directory=_ASSETS), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """
        Catch-all: serve any existing static file, otherwise return index.html
        so React handles client-side routing.
        """
        file_path = os.path.join(_DIST, full_path)
        if full_path and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(_DIST, "index.html"))
