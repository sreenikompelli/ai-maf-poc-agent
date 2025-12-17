# Azure AI Agent Deployment Commands

Complete guide to deploying an AI agent to Azure AI Foundry from scratch.

## Prerequisites

- Azure CLI installed and logged in (`az login`)
- Python 3.10+
- Owner role on the Azure subscription

---

## Step 1: Set Subscription

```bash
# List subscriptions
az account list --query "[].{Name:name, Id:id, IsDefault:isDefault}" -o table

# Set subscription
az account set --subscription "<SUBSCRIPTION_ID>"

# Verify
az account show --query "{Name:name, Id:id}" -o table
```

---

## Step 2: Create Resource Group

```bash
az group create --name "skompelli-ai-agents" --location "eastus2" -o table
```

---

## Step 3: Create Azure AI Hub

```bash
# Install/update ML extension
az extension add --name ml --upgrade --yes

# Create AI Hub
az ml workspace create \
  --kind hub \
  --name "skompelli-ai-hub" \
  --resource-group "skompelli-ai-agents" \
  --location "eastus2" \
  -o table
```

---

## Step 4: Create Azure AI Project

```bash
az ml workspace create \
  --kind project \
  --name "skompelli-ai-project" \
  --resource-group "skompelli-ai-agents" \
  --hub-id "/subscriptions/<SUBSCRIPTION_ID>/resourceGroups/skompelli-ai-agents/providers/Microsoft.MachineLearningServices/workspaces/skompelli-ai-hub" \
  --location "eastus2" \
  -o table
```

---

## Step 5: Create Azure OpenAI Resource

```bash
az cognitiveservices account create \
  --name "skompelli-openai" \
  --resource-group "skompelli-ai-agents" \
  --location "eastus2" \
  --kind "OpenAI" \
  --sku "S0" \
  --custom-domain "skompelli-openai" \
  -o table
```

---

## Step 6: Deploy GPT-4o-mini Model

```bash
az cognitiveservices account deployment create \
  --name "skompelli-openai" \
  --resource-group "skompelli-ai-agents" \
  --deployment-name "gpt-4o-mini" \
  --model-name "gpt-4o-mini" \
  --model-version "2024-07-18" \
  --model-format "OpenAI" \
  --sku-capacity 10 \
  --sku-name "Standard" \
  -o table
```

---

## Step 7: Create Azure AI Services Account (with Project Support)

```bash
# Create AI Services account with managed identity
az rest --method PUT \
  --url "https://management.azure.com/subscriptions/<SUBSCRIPTION_ID>/resourceGroups/skompelli-ai-agents/providers/Microsoft.CognitiveServices/accounts/skompelli-agent?api-version=2025-04-01-preview" \
  --body '{
    "location": "eastus2",
    "kind": "AIServices",
    "sku": {"name": "S0"},
    "identity": {"type": "SystemAssigned"},
    "properties": {
      "customSubDomainName": "skompelli-agent",
      "publicNetworkAccess": "Enabled"
    }
  }'

# Enable project management
az rest --method PATCH \
  --url "https://management.azure.com/subscriptions/<SUBSCRIPTION_ID>/resourceGroups/skompelli-ai-agents/providers/Microsoft.CognitiveServices/accounts/skompelli-agent?api-version=2025-04-01-preview" \
  --body '{"properties": {"allowProjectManagement": true}}'
```

---

## Step 8: Create Project in Azure AI Foundry Portal

**Manual Step Required:**

1. Go to [ai.azure.com](https://ai.azure.com)
2. Click **Create project**
3. Select your subscription and resource group
4. Enter project name (e.g., `skompelli-agent`)
5. Click **Create**

> Note: CLI project creation may fail with permission errors. The portal handles this automatically.

---

## Step 9: Deploy Model to Project Resource

```bash
# Find the resource name created by portal (usually ends with -resource)
az rest --method GET \
  --url "https://management.azure.com/subscriptions/<SUBSCRIPTION_ID>/resourceGroups/skompelli-ai-agents/providers/Microsoft.CognitiveServices/accounts?api-version=2025-04-01-preview" \
  --query "value[].{name:name, kind:kind}" -o table

# Deploy model to the project resource
az cognitiveservices account deployment create \
  --name "skompelli-agent-resource" \
  --resource-group "skompelli-ai-agents" \
  --deployment-name "gpt-4o-mini" \
  --model-name "gpt-4o-mini" \
  --model-version "2024-07-18" \
  --model-format "OpenAI" \
  --sku-capacity 10 \
  --sku-name "Standard" \
  -o table
```

---

## Step 10: Deploy Connection (via Bicep)

```bash
az deployment group create \
  --resource-group "skompelli-ai-agents" \
  --template-file infrastructure/modules/connections/connection.bicep \
  --parameters infrastructure/parameters/connections/skompelli-openfoodfacts.bicepparam \
  --name "openfoodfacts-connection" \
  -o table
```

---

## Step 11: Deploy Agent

```bash
# Install Python dependencies
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Deploy agent
python -m scripts.deploy_agent \
  "https://skompelli-agent-resource.services.ai.azure.com/api/projects/skompelli-agent" \
  "agents/skompelli-food-facts-agent.yaml"
```

---

## Verify Deployment

### List Agents
```bash
az rest --method GET \
  --url "https://skompelli-agent-resource.services.ai.azure.com/api/projects/skompelli-agent/agents?api-version=2024-12-01-preview" \
  --resource "https://cognitiveservices.azure.com"
```

### List Connections
```bash
az rest --method GET \
  --url "https://management.azure.com/subscriptions/<SUBSCRIPTION_ID>/resourceGroups/skompelli-ai-agents/providers/Microsoft.CognitiveServices/accounts/skompelli-agent-resource/projects/skompelli-agent/connections?api-version=2025-04-01-preview"
```

### View in Portal
1. Go to [ai.azure.com](https://ai.azure.com)
2. Select your project
3. Navigate to **Agents** to see deployed agents

---

## Configuration Files Created

| File | Purpose |
|------|---------|
| `infrastructure/parameters/connections/skompelli-openfoodfacts.bicepparam` | Connection config for skompelli subscription |
| `agents/skompelli-food-facts-agent.yaml` | Agent definition for food-facts-agent |

---

## Resource Summary

| Resource | Name | Type |
|----------|------|------|
| Resource Group | skompelli-ai-agents | Microsoft.Resources/resourceGroups |
| AI Hub | skompelli-ai-hub | Microsoft.MachineLearningServices/workspaces (hub) |
| AI Project | skompelli-ai-project | Microsoft.MachineLearningServices/workspaces (project) |
| OpenAI | skompelli-openai | Microsoft.CognitiveServices/accounts (OpenAI) |
| AI Services | skompelli-agent-resource | Microsoft.CognitiveServices/accounts (AIServices) |
| Project | skompelli-agent | Microsoft.CognitiveServices/accounts/projects |
| Model | gpt-4o-mini | OpenAI deployment |
| Connection | openfoodfacts | API connection |
| Agent | food-facts-agent | AI Agent |

---

## Cleanup (Optional)

```bash
# Delete entire resource group (removes all resources)
az group delete --name "skompelli-ai-agents" --yes --no-wait
```

---

## Troubleshooting

### "Azure AI User role" error
```bash
USER_ID=$(az ad signed-in-user show --query id -o tsv)
RESOURCE_ID=$(az resource show --resource-group skompelli-ai-agents --name skompelli-agent-resource --resource-type "Microsoft.CognitiveServices/accounts" --query id -o tsv)
az role assignment create --assignee $USER_ID --role "Azure AI User" --scope $RESOURCE_ID
```

### Project creation fails via CLI
Use the Azure AI Foundry portal at [ai.azure.com](https://ai.azure.com) to create the project manually.

### Model deployment fails
Check available models and capacity:
```bash
az cognitiveservices account list-skus --resource-group skompelli-ai-agents --name skompelli-agent-resource -o table
```
