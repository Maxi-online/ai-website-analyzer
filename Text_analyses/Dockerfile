# Text_analyses Dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Working directory
WORKDIR /app

# Copy microservice requirements/settings
COPY Text_analyses/requirements.txt Text_analyses/settings.py ./Text_analyses/

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r Text_analyses/requirements.txt

# Download NLTK data (optional; used by some analyzers)
RUN python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"

# Copy the rest of the microservice code
COPY Text_analyses/ ./Text_analyses/

# Create logs directory
RUN mkdir -p /app/logs

# Default environment variables
ENV PYTHONUNBUFFERED=1
ENV TEXT_SERVICE_PORT=8002

# Expose port
EXPOSE 8002

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8002/').read()" || exit 1

# Start application
CMD ["python", "-m", "uvicorn", "Text_analyses.main:app", "--host", "0.0.0.0", "--port", "8002"]
