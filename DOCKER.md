# Docker Setup for FabricStudio Controller

This guide explains how to run the FabricStudio Controller using Docker with interactive gcloud CLI authentication.

## Prerequisites

- Docker installed on your system
- Google Cloud project with appropriate permissions
- gcloud CLI installed (optional, for easier setup)

## Quick Start

### Option 1: Using the provided script (Recommended)

```bash
# Make the script executable (if not already done)
chmod +x run-docker.sh

# Run the container
./run-docker.sh
```

### Option 2: Manual Docker commands

```bash
# Build the image
docker build -t fabricstudio-controller .

# Run with interactive gcloud login
docker run -it -p 8000:8000 fabricstudio-controller
```

### Option 3: Using Docker Compose

```bash
# Start with docker-compose
docker-compose up

# Or run in background
docker-compose up -d
```

## First-Time Setup

When you first run the container, you'll see:

```
🔍 Checking gcloud authentication...
❌ No gcloud authentication found
Please run: gcloud auth login
Then: gcloud config set project YOUR_PROJECT_ID

Starting interactive shell...
```

### Step 1: Authenticate with Google Cloud

Inside the container, run:

```bash
# Login to Google Cloud
gcloud auth login

# Set your project
gcloud config set project YOUR_PROJECT_ID

# Verify it works
gcloud compute instances list --filter="name~^sru-fstudio-faz"
```

### Step 2: Start the application

```bash
# Start the FabricStudio Controller
python app.py
```

## Using Host gcloud Config (Easier)

If you already have gcloud authenticated on your host:

```bash
# Run with host gcloud config mounted
docker run -it -p 8000:8000 \
  -v ~/.config/gcloud:/root/.config/gcloud \
  fabricstudio-controller
```

This will automatically use your existing gcloud authentication.

## Accessing the Application

Once running, open your browser to:
- **Local**: http://localhost:8000
- **Network**: http://YOUR_SERVER_IP:8000

## Container Features

- **Interactive gcloud login**: Container starts with bash shell for authentication
- **Automatic startup**: Once authenticated, app starts automatically
- **Health checks**: Built-in health monitoring
- **Volume mounting**: Option to use host gcloud config
- **Multi-stage build**: Optimized image size

## Troubleshooting

### gcloud authentication issues

```bash
# Check authentication status
gcloud auth list

# Re-authenticate if needed
gcloud auth login --no-launch-browser

# Set project
gcloud config set project YOUR_PROJECT_ID
```

### Container won't start

```bash
# Check container logs
docker logs <container_id>

# Run container interactively for debugging
docker run -it fabricstudio-controller /bin/bash
```

### Permission issues

```bash
# Fix gcloud config permissions
sudo chown -R $USER:$USER ~/.config/gcloud
```

## Production Considerations

For production deployment:

1. **Use service accounts** instead of interactive login
2. **Set up proper secrets management**
3. **Use container orchestration** (Kubernetes, Docker Swarm)
4. **Configure proper networking and security**

## File Structure

```
FabricStudioController/
├── Dockerfile              # Container definition
├── docker-compose.yml      # Docker Compose configuration
├── .dockerignore           # Files to exclude from build
├── run-docker.sh           # Convenience script
└── DOCKER.md              # This file
```

## Commands Reference

```bash
# Build image
docker build -t fabricstudio-controller .

# Run container
docker run -it -p 8000:8000 fabricstudio-controller

# Run with host gcloud config
docker run -it -p 8000:8000 -v ~/.config/gcloud:/root/.config/gcloud fabricstudio-controller

# Run in background
docker run -d -p 8000:8000 --name fabricstudio fabricstudio-controller

# Stop container
docker stop fabricstudio

# Remove container
docker rm fabricstudio

# View logs
docker logs fabricstudio

# Execute commands in running container
docker exec -it fabricstudio /bin/bash
```
