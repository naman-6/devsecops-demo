# ==========================================================
# STAGE 1: The Builder (Isolated Compile Environment)
# ==========================================================
FROM python:3.11-slim AS builder

WORKDIR /build

# Install minimal compilation tools required for dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create a self-contained Virtual Environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ==========================================================
# STAGE 2: The Final Production Runtime (Lean & Hardened)
# ==========================================================
FROM python:3.11-slim

WORKDIR /app

# Copy the entire Virtual Environment from the builder stage
COPY --from=builder /opt/venv /opt/venv

# Activate the Virtual Environment for the runtime
ENV PATH="/opt/venv/bin:$PATH"

# Copy application source code
COPY app/ ./app

EXPOSE 8000

# Drop privileges securely (User 10001 can safely read /opt/venv)
USER 10001

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
