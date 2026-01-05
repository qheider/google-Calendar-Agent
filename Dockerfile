# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY flask_app.py .
COPY app.py .
COPY calendarTest.py .
COPY templates/ templates/
COPY static/ static/

# Create directory for credentials and token
RUN mkdir -p /app/data

# Expose port
EXPOSE 5000

# Set environment variable for Flask
ENV FLASK_APP=flask_app.py

# Run the Flask application
CMD ["python", "flask_app.py"]
