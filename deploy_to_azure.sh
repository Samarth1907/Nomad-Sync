#!/bin/bash
# Nomad-Sync Azure Container Apps Deployment Script

# ── Configuration Variables ──
RESOURCE_GROUP="NomadSync-RG"
LOCATION="eastus"
ENVIRONMENT_NAME="nomadsync-env"
ACR_NAME="nomadsyncacr$RANDOM"
BACKEND_APP_NAME="nomadsync-backend"
FRONTEND_APP_NAME="nomadsync-frontend"

# Read OpenAI Keys from environment (Make sure to export these before running!)
# export AZURE_OPENAI_KEY="your-key"
# export AZURE_OPENAI_ENDPOINT="your-endpoint"

if [ -z "$AZURE_OPENAI_KEY" ] || [ -z "$AZURE_OPENAI_ENDPOINT" ]; then
    echo "Error: AZURE_OPENAI_KEY and AZURE_OPENAI_ENDPOINT environment variables are not set."
    echo "Please run: export AZURE_OPENAI_KEY='your-key' && export AZURE_OPENAI_ENDPOINT='https://your-endpoint/'"
    exit 1
fi

echo "Starting Nomad-Sync deployment to Azure Container Apps..."

# 1. Ensure Resource Group exists
echo "Creating resource group: $RESOURCE_GROUP"
az group create --name $RESOURCE_GROUP --location $LOCATION -o none

# 2. Create Azure Container Registry (ACR)
echo "Creating Azure Container Registry: $ACR_NAME"
az acr create --resource-group $RESOURCE_GROUP --name $ACR_NAME --sku Basic --admin-enabled true -o none

# 3. Build & Push Backend Docker Image
echo "Building and pushing Backend image..."
az acr build --registry $ACR_NAME --image backend:latest ./backend

# 4. Build & Push Frontend Docker Image
echo "Building and pushing Frontend image..."
az acr build --registry $ACR_NAME --image frontend:latest ./frontend

# 5. Create Azure Container Apps Environment
echo "Creating Container Apps Environment: $ENVIRONMENT_NAME"
az containerapp env create \
  --name $ENVIRONMENT_NAME \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  -o none

# 6. Deploy Backend (Internal Ingress)
echo "Deploying Backend App..."
az containerapp create \
  --name $BACKEND_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --environment $ENVIRONMENT_NAME \
  --image $ACR_NAME.azurecr.io/backend:latest \
  --registry-server $ACR_NAME.azurecr.io \
  --ingress internal \
  --target-port 8000 \
  --env-vars "AZURE_OPENAI_KEY=$AZURE_OPENAI_KEY" "AZURE_OPENAI_ENDPOINT=$AZURE_OPENAI_ENDPOINT" "AZURE_OPENAI_DEPLOYMENT=gpt-4o" "AZURE_OPENAI_API_VERSION=2024-06-01" \
  -o none

# Retrieve internal FQDN of Backend to inject into Frontend
BACKEND_URL="http://$(az containerapp show -n $BACKEND_APP_NAME -g $RESOURCE_GROUP --query properties.configuration.ingress.fqdn -o tsv)"
echo "Backend internal URL: $BACKEND_URL"

# 7. Deploy Frontend (External Ingress)
echo "Deploying Frontend App..."
az containerapp create \
  --name $FRONTEND_APP_NAME \
  --resource-group $RESOURCE_GROUP \
  --environment $ENVIRONMENT_NAME \
  --image $ACR_NAME.azurecr.io/frontend:latest \
  --registry-server $ACR_NAME.azurecr.io \
  --ingress external \
  --target-port 8501 \
  --env-vars "BACKEND_URL=$BACKEND_URL" \
  -o none

# Final Output
FRONTEND_FQDN=$(az containerapp show -n $FRONTEND_APP_NAME -g $RESOURCE_GROUP --query properties.configuration.ingress.fqdn -o tsv)

echo ""
echo "✅ Deployment Complete!"
echo "🌐 Nomad-Sync is now live at: https://$FRONTEND_FQDN"
