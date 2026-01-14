# Docker Deployment Guide

## Overview
This Google Calendar Agent application is containerized with Docker for easy deployment and shipping.

## Prerequisites
- Docker installed (version 20.10+)
- Docker Compose installed (version 2.0+)
- Google Calendar API credentials (`Credentials.json`)
- OpenAI API key in `.env` file

## Quick Start

### 1. Build the Docker Image
```powershell
docker-compose build
```

### 2. Run the Flask Web Application
```powershell
docker-compose up -d
```

The application will be available at:
- **http://localhost:5000**
- **http://127.0.0.1:5000**

### 3. Run the CLI Application (Optional)
```powershell
docker-compose --profile cli up calendar-cli
```

## Docker Commands

### Build Image
```powershell
# Build with Docker Compose
docker-compose build

# Build with Docker directly
docker build -t google-calendar-agent:latest .
```

### Run Container
```powershell
# Run with Docker Compose (recommended)
docker-compose up -d

# Run with Docker directly
docker run -d `
  --name google-calendar-agent `
  -p 5000:5000 `
  -v "${PWD}/Credentials.json:/app/credentials.json:ro" `
  -v "${PWD}/token.pickle:/app/token.pickle" `
  -v "${PWD}/.env:/app/.env:ro" `
  google-calendar-agent:latest
```

### View Logs
```powershell
# Docker Compose
docker-compose logs -f calendar-agent

# Docker
docker logs -f google-calendar-agent
```

### Stop Container
```powershell
# Docker Compose
docker-compose down

# Docker
docker stop google-calendar-agent
docker rm google-calendar-agent
```

### Health Check
```powershell
# Check container health status
docker ps --filter name=google-calendar-agent

# Manual health check
docker exec google-calendar-agent python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000').read()"
```

## Shipping the Application

### Method 1: Save Image as TAR File
```powershell
# Build and save image
docker-compose build
docker save google-calendar-agent:latest -o google-calendar-agent.tar

# Load on target machine
docker load -i google-calendar-agent.tar
```

### Method 2: Push to Docker Registry

#### Docker Hub
```powershell
# Tag image
docker tag google-calendar-agent:latest <your-username>/google-calendar-agent:latest

# Login and push
docker login
docker push <your-username>/google-calendar-agent:latest

# Pull on target machine
docker pull <your-username>/google-calendar-agent:latest
```

#### Private Registry
```powershell
# Tag for private registry
docker tag google-calendar-agent:latest registry.example.com/google-calendar-agent:latest

# Push to private registry
docker push registry.example.com/google-calendar-agent:latest
```

### Method 3: Share Complete Package
Create a deployment package:
```powershell
# Create deployment directory
mkdir deployment
copy Dockerfile deployment/
copy docker-compose.yml deployment/
copy requirements.txt deployment/
copy flask_app.py deployment/
copy app.py deployment/
copy -r templates deployment/
copy -r static deployment/
copy .dockerignore deployment/
copy DOCKER_DEPLOYMENT.md deployment/

# Note: Do NOT include credentials.json, token.pickle, or .env
# Users must provide their own credentials
```

## Production Deployment

### Environment Variables
Create a `.env` file with:
```env
OPENAI_API_KEY=your_openai_api_key_here
FLASK_ENV=production
```

### Security Considerations
1. **Credentials**: Never include `Credentials.json` in the Docker image
2. **Tokens**: Mount `token.pickle` as a volume, not baked into image
3. **Environment**: Use `.env` file for sensitive configuration
4. **Non-root User**: The container runs as a non-root user for security
5. **Network**: Use Docker networks to isolate containers

### Resource Limits
Current configuration:
- **CPU Limit**: 1.0 core
- **Memory Limit**: 512MB
- **Reserved CPU**: 0.5 core
- **Reserved Memory**: 256MB

Adjust in `docker-compose.yml` under `deploy.resources`.

### Health Checks
- **Interval**: 30 seconds
- **Timeout**: 10 seconds
- **Retries**: 3
- **Start Period**: 40 seconds

### Logging
- **Driver**: json-file
- **Max Size**: 10MB per file
- **Max Files**: 3 files (30MB total)

## Troubleshooting

### Container Won't Start
```powershell
# Check logs
docker-compose logs calendar-agent

# Check container status
docker ps -a

# Inspect container
docker inspect google-calendar-agent
```

### Permission Issues
```powershell
# Ensure files are readable
icacls Credentials.json
icacls token.pickle

# Fix permissions if needed
icacls Credentials.json /grant:r Users:R
```

### Port Already in Use
```powershell
# Change port in docker-compose.yml
ports:
  - "8080:5000"  # Use port 8080 instead
```

### Authentication Issues
1. Ensure `Credentials.json` is valid
2. Delete `token.pickle` and re-authenticate
3. Check OAuth consent screen settings

## Updating the Application

### Update Code
```powershell
# Pull latest changes
git pull

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Update Dependencies
```powershell
# Update requirements.txt
# Then rebuild image
docker-compose build --no-cache
```

## Multi-Platform Builds

For shipping to different architectures (ARM, AMD):
```powershell
# Enable buildx
docker buildx create --use

# Build for multiple platforms
docker buildx build --platform linux/amd64,linux/arm64 `
  -t google-calendar-agent:latest `
  --push .
```

## Backup and Restore

### Backup
```powershell
# Backup token and credentials
copy token.pickle token.pickle.backup
copy Credentials.json Credentials.json.backup

# Backup Docker volume
docker run --rm `
  -v google-calendar-agent_calendar-data:/data `
  -v ${PWD}:/backup `
  busybox tar czf /backup/calendar-data-backup.tar.gz -C /data .
```

### Restore
```powershell
# Restore files
copy token.pickle.backup token.pickle
copy Credentials.json.backup Credentials.json

# Restore volume
docker run --rm `
  -v google-calendar-agent_calendar-data:/data `
  -v ${PWD}:/backup `
  busybox tar xzf /backup/calendar-data-backup.tar.gz -C /data
```

## Support

For issues or questions:
1. Check logs: `docker-compose logs -f`
2. Verify credentials are mounted correctly
3. Ensure `.env` file contains valid API keys
4. Check network connectivity to Google APIs

## Additional Resources
- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Reference](https://docs.docker.com/compose/)
- [Google Calendar API](https://developers.google.com/calendar)
