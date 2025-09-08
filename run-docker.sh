#!/bin/bash

echo "🐳 Building FabricStudio Controller Docker image..."
docker build -t fabricstudio-controller .

echo ""
echo "🚀 Starting container with persistent gcloud authentication..."
echo ""

# Create gcloud config directory if it doesn't exist
mkdir -p ~/.config/gcloud

# Check if gcloud is already authenticated on host
if gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    echo "✅ Host gcloud is authenticated, mounting config..."
    echo "   Account: $(gcloud auth list --filter=status:ACTIVE --format='value(account)')"
    echo "   Project: $(gcloud config get-value project)"
    echo ""
    docker run -it -p 8000:8000 \
        -v ~/.config/gcloud:/root/.config/gcloud \
        fabricstudio-controller
else
    echo "⚠️  Host gcloud not authenticated, starting interactive container..."
    echo "   Authentication will be saved to ~/.config/gcloud for future use"
    echo ""
    docker run -it -p 8000:8000 \
        -v ~/.config/gcloud:/root/.config/gcloud \
        fabricstudio-controller
fi
