# Kiwi_AI - Advanced Adaptive Algorithmic Trading System
# Production Dockerfile

FROM python:3.11-slim

# Set metadata
LABEL maintainer="@Noobiez16"
LABEL description="Kiwi_AI - Adaptive Algorithmic Trading System"
LABEL version="0.3.0"

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/logs \
    /app/models \
    /app/market_data \
    /app/backtest_reports

# Create non-root user for security
RUN useradd -m -u 1000 kiwi && \
    chown -R kiwi:kiwi /app

# Switch to non-root user
USER kiwi

# Expose port for dashboard (if needed)
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Default command (can be overridden)
CMD ["python", "main.py"]
