"""FastAPI application and optional production frontend hosting."""

from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles

from urban_environment.utils.config import load_cities
from urban_environment.web.api import router
from urban_environment.web.queries import AnalyticsRepository, AnalyticsUnavailableError


ROOT = Path(__file__).resolve().parents[3]


def create_app(
    *,
    database_path: Path | None = None,
    cities_path: Path | None = None,
    frontend_dir: Path | None = None,
) -> FastAPI:
    app = FastAPI(
        title="Urban Environment Analytics API",
        version="1.0.0",
        description="Read-only weather, air-quality, quality and pipeline analytics.",
    )
    app.state.repository = AnalyticsRepository(
        database_path or ROOT / "data" / "analytics" / "environment.duckdb"
    )
    app.state.cities = load_cities(cities_path or ROOT / "config" / "cities.json")
    app.include_router(router)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
        allow_methods=["GET"],
        allow_headers=["*"],
    )

    @app.exception_handler(AnalyticsUnavailableError)
    async def unavailable(_: Request, exc: AnalyticsUnavailableError) -> JSONResponse:
        return JSONResponse(status_code=503, content={"detail": str(exc)})

    web_root = frontend_dir or ROOT / "frontend" / "dist"
    assets = web_root / "assets"
    if assets.exists():
        app.mount("/assets", StaticFiles(directory=assets), name="assets")

    @app.get("/", include_in_schema=False, response_model=None)
    def root() -> FileResponse | RedirectResponse:
        index = web_root / "index.html"
        return FileResponse(index) if index.exists() else RedirectResponse("/docs")

    @app.get("/{path:path}", include_in_schema=False, response_model=None)
    def spa(path: str) -> FileResponse | JSONResponse:
        index = web_root / "index.html"
        if index.exists() and not path.startswith("api/"):
            return FileResponse(index)
        return JSONResponse(status_code=404, content={"detail": "Not found"})

    return app


app = create_app()
