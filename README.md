# Nomad-Sync

A minimal, working prototype of a multi-agent travel planning system. 

## Architecture
Nomad-Sync uses three agents, one API service, and a containerized deployment on Azure.

### Agents
1. **Planner Agent (Azure OpenAI)**
   - Creates a structured travel itinerary plan using GPT-4o.
2. **Retriever Agent (Azure Maps)**
   - Fetches points of interest (POIs) based on the plan.
3. **Executor Agent**
   - Generates a compiled PDF trip itinerary for the user.

### Technologies
- **Backend API**: FastAPI, Python 3.11
- **Frontend App**: Streamlit
- **Infrastructure**: Azure OpenAI, Azure Maps, Azure Container Apps, Azure Container Registry (ACR), Azure Blob Storage, and Azure Key Vault.

## Getting Started

### Prerequisites
- Python 3.11+
- Docker
- Azure CLI

### Environment Variables
Store the following in Azure Key Vault (referenced by Container Apps at runtime) or export them locally for development:
- `AZURE_OPENAI_KEY`
- `AZURE_OPENAI_ENDPOINT`
- `AZURE_MAPS_KEY`

### Local Setup
1. **Backend**:
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn main:app --host 0.0.0.0 --port 8000
   ```
2. **Frontend**:
   ```bash
   cd frontend
   pip install -r requirements.txt
   streamlit run app.py
   ```

## Demo Flow
1. User opens the Streamlit frontend.
2. Input parameters (e.g., Chennai → Mahabalipuram, 2 days, ₹5000).
3. **Pipeline execution**:
   - Planner → create itinerary
   - Retriever → fetch POIs
   - Executor → generate PDF
   - Frontend → show results

## What Judges See
Working system with:
- AI planner
- Real map data
- Optimized itinerary
- Downloadable trip plan
- Scalable cloud architecture

This satisfies:
- Multi-agent architecture
- Real APIs
- Container deployment
- Azure usage