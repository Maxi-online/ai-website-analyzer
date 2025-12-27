# SEO_analyses Dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Working directory
WORKDIR /app

# Copy requirements.txt and settings.py from the microservice
COPY SEO_analyses/requirements.txt SEO_analyses/settings.py ./SEO_analyses/

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r SEO_analyses/requirements.txt

# Copy the rest of the microservice files
COPY SEO_analyses/ ./SEO_analyses/

# Create logs directory
RUN mkdir -p /app/logs

# Default environment variables
ENV PYTHONUNBUFFERED=1
ENV SEO_SERVICE_PORT=8001

# Expose port
EXPOSE 8001

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8001/').read()" || exit 1

# Start the application
CMD ["python", "-m", "uvicorn", "SEO_analyses.main:app", "--host", "0.0.0.0", "--port", "8001"]
