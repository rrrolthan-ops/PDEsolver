# Production Dockerfile for the backend.
# Distinct from backend.Dockerfile (dev) because production:
# - doesn't install dev dependencies (no pytest, ruff)
# - copies only what's needed (no .git, no tests, etc.)
# - uses a non-root user
# - removes the build toolchain after wheels are installed

FROM python:3.11-slim AS builder

WORKDIR /build

# Build deps for native wheels.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./
# Install into a target directory so we can copy the site-packages
# tree into the final image without dragging the build toolchain.
RUN pip install --no-cache-dir --prefix=/install .

# ---------------------------------------------------------------------
# Runtime image
# ---------------------------------------------------------------------
FROM python:3.11-slim

WORKDIR /app

# Copy installed packages from the builder stage.
COPY --from=builder /install /usr/local

# Copy the app code (NOT pyproject — already installed above; NOT tests).
COPY app ./app

# Run as a non-root user.
RUN groupadd -g 1000 app && useradd -u 1000 -g app -s /bin/bash app \
    && mkdir -p /app/data && chown -R app:app /app
USER app

# SQLite path: persisted via a mounted volume.
ENV DATABASE_URL=sqlite:///./data/pdesolver.db
# Quiet noisy SymPy deprecation warnings in production logs.
ENV PYTHONWARNINGS=ignore::DeprecationWarning
EXPOSE 8000

# Production: no --reload. Workers default to 2 — adjust at deploy time.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
