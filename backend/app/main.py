"""FastAPI application entrypoint."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes_problems import router as problems_router

app = FastAPI(
    title="PDESolver Pedagógico",
    description=(
        "Symbolic solver for classical PDEs with step-by-step pedagogical output. "
        "Phase 1: heat equation 1D by separation of variables."
    ),
    version="0.1.0",
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
