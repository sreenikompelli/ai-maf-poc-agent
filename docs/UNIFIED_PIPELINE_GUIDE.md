# Unified Azure DevOps Pipeline Guide

## Overview

Single pipeline (`azure-devops-pipeline.yml`) that deploys all AI Foundry components with:
- ✅ Runtime checkboxes for selective deployment
- ✅ Correct deployment order (guardrails → connections → agents)
- ✅ Dependency validation
- ✅ Error handling for missing dependencies

## Pipeline Structure

```
azure-devops-pipeline.yml
├── Stage 1: Deploy Guardrails 🛡️
│   └── Content filters & PII protection
│
├── Stage 2: Deploy Connections 🔌
│   └── API tool connections (depends on Stage 1)
│
├── Stage 3: Deploy Agents 🤖
│   ├── Validate dependencies
│   └── Deploy agent (depends on Stages 1 & 2)
│
└── Stage 4: Summary 📊
    └── Show deployment results
```

## Runtime Parameters

When you run the pipeline manually, you'll see these checkboxes:

| Parameter | Description | Default |
|-----------|-------------|---------|
| **Deploy Guardrails** | Deploy content filters & PII protection | ✅ Yes |
| **Deploy Connections** | Deploy API tool connections | ✅ Yes |
| **Deploy Agents** | Deploy AI agents | ✅ Yes |
| **Agent File** | Specific agent file to deploy | `agents/weather-agent.yaml` |

## Usage Scenarios

### Scenario 1: Full Deployment (Default)
**Use case**: First-time setup or complete refresh

**Settings**:
- ✅ Deploy Guardrails
- ✅ Deploy Connections
- ✅ Deploy Agents

**Result**: Deploys everything in order

---

### Scenario 2: Guardrails Only
**Use case**: Update content filter settings

**Settings**:
- ✅ Deploy Guardrails
- ❌ Deploy Connections
- ❌ Deploy Agents

**Result**: Only updates guardrails

---

### Scenario 3: Connections Only
**Use case**: Add new API tool

**Settings**:
- ❌ Deploy Guardrails
- ✅ Deploy Connections
- ❌ Deploy Agents

**Result**: Only deploys connections

---

### Scenario 4: Agent Only (with validation)
**Use case**: Update agent configuration

**Settings**:
- ❌ Deploy Guardrails
- ❌ Deploy Connections
- ✅ Deploy Agents

**Result**: 
- ✅ Deploys agent if dependencies exist
- ❌ **FAILS** if agent requires connections that don't exist

---

### Scenario 5: Connections + Agents
**Use case**: New agent with new tool

**Settings**:
- ❌ Deploy Guardrails
- ✅ Deploy Connections
- ✅ Deploy Agents

**Result**: Deploys connection first, then agent

---

## Dependency Validation

### What Gets Validated

The pipeline automatically checks:

1. **Agent file exists**
   ```yaml
   # If agent file not found → FAIL
   ```

2. **Required connections**
   ```yaml
   # Agent YAML:
   tools:
     - type: openapi
       options:
         connection_id: weathertool  # ← Pipeline checks this exists
   ```

3. **Deployment order**
   ```
   If agent needs connections → connections must be deployed first
   ```

### Validation Logic

```python
# Pseudo-code of what happens
if agent_requires_connections and not deploy_connections_selected:
    if connections_already_exist_in_azure:
        ✅ PASS - use existing connections
    else:
        ❌ FAIL - connections missing!
```

### Error Messages

**Missing Connection**:
```
❌ ERROR: Agent requires connections but 'Deploy Connections' was not selected!
   Required connections: weathertool
   
   Please either:
   1. Enable 'Deploy Connections' checkbox, OR
   2. Ensure connections are already deployed
```

**Missing Agent File**:
```
❌ Agent file not found: agents/my-agent.yaml
```

---

## How to Run

### Option 1: Manual Run (Azure DevOps UI)

1. Go to Azure DevOps → Pipelines
2. Select `azure-devops-pipeline`
3. Click **Run pipeline**
4. Check/uncheck deployment options:
   ```
   ☑ Deploy Guardrails
   ☑ Deploy Connections
   ☑ Deploy Agents
   ```
5. Specify agent file (optional):
   ```
   agents/weather-agent.yaml
   ```
6. Click **Run**

### Option 2: Azure CLI

```bash
# Full deployment
az pipelines run \
  --name azure-devops-pipeline \
  --branch main \
  --parameters \
    deployGuardrails=true \
    deployConnections=true \
    deployAgents=true \
    agentFile=agents/weather-agent.yaml

# Guardrails only
az pipelines run \
  --name azure-devops-pipeline \
  --branch main \
  --parameters \
    deployGuardrails=true \
    deployConnections=false \
    deployAgents=false

# Agent only (will validate dependencies)
az pipelines run \
  --name azure-devops-pipeline \
  --branch main \
  --parameters \
    deployGuardrails=false \
    deployConnections=false \
    deployAgents=true \
    agentFile=agents/weather-agent.yaml
```

### Option 3: Automatic Trigger

Pipeline auto-runs when you push changes to:
- `infrastructure/**`
- `agents/**`
- `scripts/**`
- `azure-devops-pipeline.yml`

**Default behavior**: Deploys everything

---

## Stage Dependencies

### Dependency Graph

```
DeployGuardrails (Stage 1)
    ↓
DeployConnections (Stage 2)
    ↓
DeployAgents (Stage 3)
    ↓
DeploymentSummary (Stage 4)
```

### Conditional Execution

**Stage 2 runs if**:
- `deployConnections = true` AND
- (Stage 1 succeeded OR `deployGuardrails = false`)

**Stage 3 runs if**:
- `deployAgents = true` AND
- (Stages 1 & 2 succeeded OR both were skipped)

**Stage 4 always runs** to show summary

---

## Deployment Order

### Why This Order Matters

1. **Guardrails First** 🛡️
   - Sets up content filtering
   - Must exist before agents use them
   - Independent of other components

2. **Connections Second** 🔌
   - Deploys API tool connections
   - Agents reference these connections
   - Can use guardrails if deployed

3. **Agents Last** 🤖
   - References connections by ID
   - Protected by guardrails
   - Depends on both previous stages

### Example Flow

```yaml
# Agent YAML references connection
tools:
  - type: openapi
    connection_id: weathertool  # ← Must exist before agent deploys

# Pipeline ensures:
1. Deploy connection "weathertool" (Stage 2)
2. Then deploy agent (Stage 3)
```

---

## Troubleshooting

### Issue: Agent deployment fails with "connection not found"

**Cause**: Agent requires connection but it wasn't deployed

**Solution**:
1. Enable "Deploy Connections" checkbox, OR
2. Manually deploy connection first:
   ```bash
   python3 scripts/deploy_infrastructure.py foundry_connection \
     --bicepparam infrastructure/parameters/connections/connections.bicepparam
   ```

---

### Issue: Pipeline skips stages

**Cause**: Dependency conditions not met

**Solution**: Check stage conditions:
- Stage 2 needs Stage 1 to succeed (or be skipped)
- Stage 3 needs Stages 1 & 2 to succeed (or be skipped)

---

### Issue: Validation fails but resources exist

**Cause**: Validation script can't detect existing resources

**Solution**: 
1. Deploy connections in pipeline to ensure they exist
2. Or update validation script to check Azure directly

---

## Pipeline Variables

### Required Variables

Set these in Azure DevOps → Pipelines → Variables:

| Variable | Value | Description |
|----------|-------|-------------|
| `AZURE_SERVICE_CONNECTION` | `ado-service-connection` | Azure service connection name |
| `RESOURCE_GROUP` | `ad-usa-poc` | Resource group name |
| `AI_FOUNDRY_ENDPOINT` | `https://...` | AI Foundry project endpoint |

### How to Set

1. Go to Pipeline → Edit
2. Click **Variables** (top right)
3. Add/update variables
4. Save

---

## Monitoring

### View Deployment Progress

1. Go to Azure DevOps → Pipelines
2. Click on running pipeline
3. See stages:
   ```
   🛡️ Deploy Guardrails     ✅ Succeeded
   🔌 Deploy Connections    ✅ Succeeded
   🤖 Deploy Agents         🔄 Running...
   📊 Deployment Summary    ⏳ Pending
   ```

### Check Logs

Click on any stage → Job → Step to see detailed logs

---

## Best Practices

### 1. First-Time Setup
```
✅ Deploy Guardrails
✅ Deploy Connections
✅ Deploy Agents
```

### 2. Update Guardrails Only
```
✅ Deploy Guardrails
❌ Deploy Connections
❌ Deploy Agents
```

### 3. Add New Agent
```
❌ Deploy Guardrails (already exist)
✅ Deploy Connections (if new tool needed)
✅ Deploy Agents
```

### 4. Update Existing Agent
```
❌ Deploy Guardrails
❌ Deploy Connections
✅ Deploy Agents
```

---

## Migration from Old Pipelines

### Old Structure
```
pipelines/
├── infrastructure-pipeline.yml  ❌ Delete
├── guardrails-pipeline.yml      ❌ Delete
└── agent-pipeline.yml           ❌ Delete
```

### New Structure
```
azure-devops-pipeline.yml  ✅ Use this
```

### Migration Steps

1. Create new pipeline in Azure DevOps
2. Point to `azure-devops-pipeline.yml`
3. Test with manual run
4. Delete old pipelines once verified

---

## Summary

✅ **Single pipeline** for all deployments
✅ **Runtime checkboxes** for selective deployment
✅ **Dependency validation** prevents errors
✅ **Correct order** guaranteed (guardrails → connections → agents)
✅ **Error handling** for missing dependencies
✅ **Flexible** - deploy one, some, or all components

**Next**: Set up pipeline in Azure DevOps and test!
