"""FastAPI application entrypoint."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes_library import router as library_router
from app.api.routes_parse import router as parse_router
from app.api.routes_problems import router as problems_router
from app.api.routes_vision import router as vision_router
from app.db.session import init_db


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Create SQLite tables on startup. Idempotent.
    init_db()
    yield


app = FastAPI(
    title="PDESolver Pedagógico",
    description=(
        "Symbolic solver for classical PDEs with step-by-step pedagogical "
        "output. Phase 5: PDF export and problem library."
    ),
    version="0.5.0",
    lifespan=lifespan,
)

# In production behind a reverse proxy this would be tightened.
# For local dev we allow the Vite dev server.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


app.include_router(problems_router)
app.include_router(parse_router)
app.include_router(vision_router)
app.include_router(library_router)
