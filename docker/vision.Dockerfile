# Placeholder Dockerfile for the Phase 4 vision microservice.
# Activate by uncommenting the `vision:` service in docker-compose.yml.
#
# This container intentionally lives apart from the main backend
# because it pulls in PyTorch + transformers (~3 GB of dependencies)
# that the symbolic solver doesn't need.

FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1 libglib2.0-0 \
    poppler-utils \
    tesseract-ocr \
    tesseract-ocr-spa \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml ./
RUN pip install --no-cache-dir -e ".[dev,vision,llm]"

# Phase 4 will add:
# RUN pip install --no-cache-dir pix2tex transformers torch easyocr pytesseract

COPY . .

EXPOSE 8001

CMD ["uvicorn", "app.vision_main:app", "--host", "0.0.0.0", "--port", "8001"]
