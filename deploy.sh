#!/bin/bash

echo "🚀 FabricStudio Controller Deployment Script"
echo "============================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ Google Cloud CLI is not installed. Please install it first."
    echo "   Visit: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if gcloud is authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "⚠️  gcloud is not authenticated. Please run:"
    echo "   gcloud auth login"
    echo "   gcloud config set project YOUR_PROJECT_ID"
    exit 1
fi

echo "✅ Prerequisites check passed"
echo "   Docker: $(docker --version)"
echo "   gcloud: $(gcloud --version | head -1)"
echo "   Account: $(gcloud auth list --filter=status:ACTIVE --format='value(account)')"
echo "   Project: $(gcloud config get-value project)"
echo ""

# Build the image
echo "🔨 Building Docker image..."
docker build -t fabricstudio-controller .

# Stop existing container if running
if docker ps -q --filter "name=fabricstudio" | grep -q .; then
    echo "🛑 Stopping existing container..."
    docker stop fabricstudio
    docker rm fabricstudio
fi

# Start the container
echo "🚀 Starting FabricStudio Controller..."
docker run -d -p 8000:8000 --name fabricstudio \
  -v ~/.config/gcloud:/root/.config/gcloud \
  fabricstudio-controller

# Wait for startup
echo "⏳ Waiting for application to start..."
sleep 5

# Check if it's running
if docker ps --filter "name=fabricstudio" --filter "status=running" | grep -q fabricstudio; then
    echo "✅ FabricStudio Controller is running!"
    echo "   🌐 Open your browser to: http://localhost:8000"
    echo ""
    echo "📋 Container management:"
    echo "   View logs: docker logs fabricstudio"
    echo "   Stop: docker stop fabricstudio"
    echo "   Start: docker start fabricstudio"
    echo "   Remove: docker stop fabricstudio && docker rm fabricstudio"
else
    echo "❌ Failed to start container. Check logs:"
    docker logs fabricstudio
    exit 1
fi
