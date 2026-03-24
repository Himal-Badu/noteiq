FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application (exclude unnecessary files)
COPY noteiq/ noteiq/
COPY api/ api/
COPY cli/ cli/
COPY tests/ tests/
COPY app.py .
COPY setup.py .
COPY README.md .

# Create storage directory
RUN mkdir -p /app/data

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV STORAGE_FILE=/app/data/notes.json

# Expose port
EXPOSE 8000

# Default command
CMD ["python", "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
