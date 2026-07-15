# Dockerfile for backend service
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Add non-root system user and group for security hardening (OWASP/CIS compliance)
RUN groupadd -g 10001 appgroup && \
    useradd -u 10001 -g appgroup -d /app -s /sbin/nologin -c "Application User" appuser

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application directories
COPY api/ ./api/
COPY src/ ./src/
COPY models/ ./models/
COPY data/ ./data/

# Adjust ownership of execution workspace
RUN chown -R appuser:appgroup /app

# Define runtime user contexts and port exposures
EXPOSE 8000
USER appuser

CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
