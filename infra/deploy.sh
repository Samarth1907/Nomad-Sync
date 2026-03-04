#!/bin/bash
# Nomad-Sync Azure Deployment Script

# 1. Create container registry
echo "Creating Azure Container Registry..."
az acr create \
 --resource-group nomadsync-rg \
 --name nomadsyncreg \
 --sku Basic

# 2. Build container
echo "Building Docker container for the backend..."
docker build -t nomadsync-backend ../backend

# 3. Push image
echo "Pushing Docker image to ACR..."
docker tag nomadsync-backend nomadsyncreg.azurecr.io/nomadsync-backend
docker push nomadsyncreg.azurecr.io/nomadsync-backend

# 4. Deploy to Container Apps
echo "Deploying to Azure Container Apps..."
az containerapp create \
 --name nomadsync-api \
 --resource-group nomadsync-rg \
 --image nomadsyncreg.azurecr.io/nomadsync-backend \
 --target-port 8000 \
 --ingress external

echo "Deployment complete."
