#!/bin/bash

echo "🔐 Setting up persistent gcloud authentication for Docker..."
echo ""

# Create gcloud config directory
mkdir -p ~/.config/gcloud

echo "Choose your authentication method:"
echo "1) Use existing host gcloud authentication"
echo "2) Set up new authentication in container"
echo ""
read -p "Enter choice (1 or 2): " choice

case $choice in
    1)
        echo ""
        echo "✅ Using existing host gcloud authentication..."
        echo "   Account: $(gcloud auth list --filter=status:ACTIVE --format='value(account)')"
        echo "   Project: $(gcloud config get-value project)"
        echo ""
        echo "Starting container with persistent authentication..."
        docker run -it -p 8000:8000 \
            -v ~/.config/gcloud:/root/.config/gcloud \
            fabricstudio-controller
        ;;
    2)
        echo ""
        echo "🚀 Starting container for interactive authentication..."
        echo "   After authentication, your credentials will be saved to ~/.config/gcloud"
        echo ""
        docker run -it -p 8000:8000 \
            -v ~/.config/gcloud:/root/.config/gcloud \
            fabricstudio-controller
        ;;
    *)
        echo "❌ Invalid choice. Please run the script again."
        exit 1
        ;;
esac
