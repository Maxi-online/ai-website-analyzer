# Senior_analyser Dockerfile
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Working directory
WORKDIR /app

# Copy requirements.txt and settings.py from the microservice
COPY Senior_analyser/requirements.txt Senior_analyser/settings.py ./Senior_analyser/

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r Senior_analyser/requirements.txt

# Copy the rest of the microservice files
COPY Senior_analyser/ ./Senior_analyser/

# Create logs directory
RUN mkdir -p /app/logs

# Default environment variables
ENV PYTHONUNBUFFERED=1
ENV SENIOR_SERVICE_PORT=8004

# Expose port
EXPOSE 8004

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8004/').read()" || exit 1

# Start the application
CMD ["python", "-m", "uvicorn", "Senior_analyser.main:app", "--host", "0.0.0.0", "--port", "8004"]
