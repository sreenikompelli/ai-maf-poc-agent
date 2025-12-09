# Infrastructure Folder Structure

## Overview

Clean, organized structure with 1:1 mapping between modules and parameters.

## Structure

```
infrastructure/
├── modules/                          # Reusable Bicep templates
│   ├── connections/                  # Connection module
│   │   ├── connection.bicep          # Template
│   │   └── api.json                  # OpenAPI spec (reference)
│   │
│   └── guardrails/                   # Guardrails module
│       └── content_filter.bicep      # Template
│
└── parameters/                       # Configuration files (1:1 with modules)
    ├── connections/                  # Connection parameters
    │   ├── connections.bicepparam    # Main config
    │   └── api.json                  # OpenAPI spec (actual)
    │
    └── guardrails/                   # Guardrails parameters
        └── guardrails.bicepparam     # Main config
```

## Design Principles

### 1. Separation of Concerns
- **modules/**: Infrastructure templates (code)
- **parameters/**: Configuration data (data)

### 2. 1:1 Mapping
Each module has a corresponding parameters folder:
- `modules/connections/` → `parameters/connections/`
- `modules/guardrails/` → `parameters/guardrails/`

### 3. Self-Contained Parameters
Each parameters folder contains:
- `.bicepparam` file(s)
- Supporting data files (JSON, YAML, etc.)

### 4. Relative Paths
Parameters reference modules using relative paths:
```bicep
using '../../modules/connections/connection.bicep'
```

## Module Details

### Connections Module

**Purpose**: Deploy API connections to Azure AI Foundry

**Files**:
- `modules/connections/connection.bicep` - Bicep template
- `modules/connections/api.json` - OpenAPI spec (reference copy)

**Parameters**:
- `parameters/connections/connections.bicepparam` - Configuration
- `parameters/connections/api.json` - OpenAPI spec (actual source)

**Deployment**:
```bash
python scripts/deploy_infrastructure.py foundry_connection \
  --bicepparam infrastructure/parameters/connections/connections.bicepparam
```

### Guardrails Module

**Purpose**: Deploy content filtering and PII protection

**Files**:
- `modules/guardrails/content_filter.bicep` - Bicep template

**Parameters**:
- `parameters/guardrails/guardrails.bicepparam` - Configuration

**Deployment**:
```bash
python3 scripts/deploy_guardrails.py nonprod
```

## Adding New Modules

### Step 1: Create Module
```bash
mkdir infrastructure/modules/my-module
# Create your .bicep template
```

### Step 2: Create Parameters Folder
```bash
mkdir infrastructure/parameters/my-module
```

### Step 3: Create Parameter File
```bicep
// infrastructure/parameters/my-module/my-module.bicepparam
using '../../modules/my-module/my-module.bicep'

param setting1 = 'value1'
param setting2 = 'value2'
```

### Step 4: Deploy
```bash
az deployment group create \
  --resource-group ad-usa-poc \
  --template-file infrastructure/modules/my-module/my-module.bicep \
  --parameters infrastructure/parameters/my-module/my-module.bicepparam
```

## Environment-Specific Configurations

### Option 1: Multiple Parameter Files (Recommended for simple cases)
```
parameters/guardrails/
├── guardrails.bicepparam       # Default/nonprod
├── guardrails-dev.bicepparam   # Development
└── guardrails-prod.bicepparam  # Production
```

### Option 2: Environment Folders (Recommended for complex cases)
```
parameters/guardrails/
├── base.bicepparam             # Shared defaults
├── dev/
│   └── guardrails.bicepparam   # Dev overrides
├── test/
│   └── guardrails.bicepparam   # Test overrides
└── prod/
    └── guardrails.bicepparam   # Prod overrides
```

### Option 3: Single File with Variables (Simplest)
```bicep
// Use deployment-time parameters
param environment string = 'nonprod'

var severityByEnv = {
  dev: 'low'
  nonprod: 'medium'
  prod: 'high'
}

param severity = severityByEnv[environment]
```

## File Naming Conventions

### Modules
- Use descriptive names: `connection.bicep`, `content_filter.bicep`
- One primary template per module folder
- Supporting files: `api.json`, `schema.json`, etc.

### Parameters
- Match module name: `connections.bicepparam`, `guardrails.bicepparam`
- Environment suffix optional: `guardrails-prod.bicepparam`
- Supporting data files: `api.json`, `config.yaml`, etc.

## Path References

### From Parameters to Modules
```bicep
// Always use relative paths from parameters/ to modules/
using '../../modules/connections/connection.bicep'
```

### Loading Data Files
```bicep
// Load from same directory
param openApiSpec = loadTextContent('./api.json')

// Load from parent directory
param config = loadJsonContent('../shared/config.json')
```

## Benefits of This Structure

1. ✅ **Clear Organization**: Easy to find related files
2. ✅ **Scalable**: Add modules without restructuring
3. ✅ **Maintainable**: 1:1 mapping is intuitive
4. ✅ **Flexible**: Support multiple environments
5. ✅ **Self-Documenting**: Structure explains purpose

## Migration from Old Structure

### Old Structure
```
infrastructure/
├── modules/foundry_connection/
│   ├── connection.bicep
│   └── api.json
├── parameters/
│   ├── connections.bicepparam
│   └── guardrails.bicepparam
```

### New Structure
```
infrastructure/
├── modules/
│   ├── connections/
│   │   ├── connection.bicep
│   │   └── api.json
│   └── guardrails/
│       └── content_filter.bicep
├── parameters/
│   ├── connections/
│   │   ├── connections.bicepparam
│   │   └── api.json
│   └── guardrails/
│       └── guardrails.bicepparam
```

### Migration Steps
1. ✅ Create new folder structure
2. ✅ Move files to new locations
3. ✅ Update relative paths in `.bicepparam` files
4. ✅ Update deployment scripts
5. ✅ Test deployments
6. ✅ Remove old structure

## Examples

### Example 1: Deploy Connections
```bash
# Using new structure
python scripts/deploy_infrastructure.py foundry_connection \
  --bicepparam infrastructure/parameters/connections/connections.bicepparam
```

### Example 2: Deploy Guardrails
```bash
# Using new structure
python3 scripts/deploy_guardrails.py nonprod
# Script internally uses: infrastructure/parameters/guardrails/guardrails.bicepparam
```

### Example 3: Add New Module
```bash
# 1. Create module
mkdir -p infrastructure/modules/monitoring
cat > infrastructure/modules/monitoring/app_insights.bicep << 'EOF'
param name string
param location string
resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: name
  location: location
  kind: 'web'
}
EOF

# 2. Create parameters
mkdir -p infrastructure/parameters/monitoring
cat > infrastructure/parameters/monitoring/monitoring.bicepparam << 'EOF'
using '../../modules/monitoring/app_insights.bicep'
param name = 'ai-agents-insights'
param location = 'eastus2'
EOF

# 3. Deploy
az deployment group create \
  --resource-group ad-usa-poc \
  --template-file infrastructure/modules/monitoring/app_insights.bicep \
  --parameters infrastructure/parameters/monitoring/monitoring.bicepparam
```

## Summary

**Clean, organized, scalable structure with:**
- Clear separation: modules (code) vs parameters (data)
- 1:1 mapping: each module has a parameters folder
- Easy to navigate: find related files quickly
- Simple to extend: add new modules without refactoring
