# ═══════════════════════════════════════════════════════════════════
# SafeHaven — Multi-stage Docker build
#
# Stage 1 (builder):  Node 20 — installs deps and builds React frontend
# Stage 2 (runtime):  Python 3.13 slim — runs FastAPI, serves everything
#
# The final image exposes port 8000 and serves:
#   /api/*     → FastAPI endpoints (agents, incidents, etc.)
#   /          → React SPA (built static files)
# ═══════════════════════════════════════════════════════════════════

# ── Stage 1: Build React frontend ──────────────────────────────────
FROM node:20-alpine AS builder

WORKDIR /frontend

# Install dependencies first (layer caching)
COPY dashboard/frontend/package*.json ./
RUN npm ci --legacy-peer-deps

# Copy source and build
COPY dashboard/frontend/ ./
RUN npm run build
# Output: /frontend/dist/


# ── Stage 2: Python runtime ─────────────────────────────────────────
FROM python:3.13-slim AS runtime

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd --create-home --shell /bin/bash safehaven
WORKDIR /app

# Install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy project source (exclude .venv, node_modules via .dockerignore)
COPY . .

# Copy built frontend from Stage 1 into the location FastAPI serves
COPY --from=builder /frontend/dist ./dashboard/frontend/dist

# Create state directory (persists incidents.jsonl + audit.jsonl at runtime)
RUN mkdir -p state && chown -R safehaven:safehaven /app

# Switch to non-root user
USER safehaven

# Expose API port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health')"

# Run FastAPI with uvicorn
CMD ["uvicorn", "dashboard.api:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
