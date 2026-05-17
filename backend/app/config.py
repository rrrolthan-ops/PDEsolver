"""Runtime configuration loaded from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    backend_host: str = os.getenv("BACKEND_HOST", "0.0.0.0")
    backend_port: int = int(os.getenv("BACKEND_PORT", "8000"))
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./data/pdesolver.db")

    anthropic_api_key: str | None = os.getenv("ANTHROPIC_API_KEY") or None
    mathpix_api_key: str | None = os.getenv("MATHPIX_API_KEY") or None
    mathpix_app_id: str | None = os.getenv("MATHPIX_APP_ID") or None


settings = Settings()
