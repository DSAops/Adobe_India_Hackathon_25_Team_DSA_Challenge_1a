# Use Python 3.11 slim image as base with explicit AMD64 platform
FROM --platform=linux/amd64 python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgtk-3-0 \
    libfontconfig1 \
    libfreetype6-dev \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY *.py ./
COPY patterns.yaml ./

# Create input and output directories
RUN mkdir -p input output

# Set permissions
RUN chmod -R 755 /app

# Create a non-root user (optional, for security)
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose any ports if needed (not required for this script)
# EXPOSE 8000

# Default command
CMD ["python", "main.py"]
