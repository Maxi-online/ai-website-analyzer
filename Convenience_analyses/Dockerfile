# Convenience_analyses Dockerfile
FROM python:3.11-slim

# Install system dependencies (Chromium is optional; kept for legacy/compat)
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    wget \
    gnupg \
    unzip \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# Working directory
WORKDIR /app

# Copy microservice requirements/settings
COPY Convenience_analyses/requirements.txt Convenience_analyses/settings.py ./Convenience_analyses/

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r Convenience_analyses/requirements.txt

# Copy the rest of the microservice code
COPY Convenience_analyses/ ./Convenience_analyses/

# Create logs directory
RUN mkdir -p /app/logs

# Default environment variables
ENV PYTHONUNBUFFERED=1
ENV CONVENIENCE_SERVICE_PORT=8003
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

# Expose port
EXPOSE 8003

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8003/').read()" || exit 1

# Start application
CMD ["python", "-m", "uvicorn", "Convenience_analyses.main:app", "--host", "0.0.0.0", "--port", "8003"]
