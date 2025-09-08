#!/bin/bash

echo "🐳 Building FabricStudio Controller Docker image..."
docker build -t fabricstudio-controller .

echo ""
echo "🚀 Starting container with interactive gcloud login..."
echo ""

# Check if gcloud is already authenticated on host
if gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "✅ Host gcloud is authenticated, mounting config..."
    docker run -it -p 8000:8000 \
        -v ~/.config/gcloud:/root/.config/gcloud \
        fabricstudio-controller
else
    echo "⚠️  Host gcloud not authenticated, starting interactive container..."
    echo "You'll need to run 'gcloud auth login' inside the container"
    echo ""
    docker run -it -p 8000:8000 \
        fabricstudio-controller
fi
