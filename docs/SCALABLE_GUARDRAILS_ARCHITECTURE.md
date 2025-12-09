# Scalable Guardrails Architecture

## Problem Statement

As you add more guardrails (content filtering, PII protection, prompt injection, etc.), you need:
- ✅ Easy to add new filters
- ✅ Environment-specific configurations (dev, test, prod)
- ✅ Reusable components
- ✅ Clear separation of concerns
- ✅ Simple deployment

## Recommended Architecture

### Structure

```
infrastructure/
├── modules/
│   └── guardrails/
│       ├── rai_policy.bicep              # Main RAI policy module
│       ├── content_filters.bicep         # Content filtering logic
│       ├── pii_filters.bicep             # PII filtering logic
│       └── prompt_shields.bicep          # Prompt injection protection
│
├── parameters/
│   ├── base/                             # Base configurations
│   │   ├── content_filters_base.bicepparam
│   │   ├── pii_filters_base.bicepparam
│   │   └── prompt_shields_base.bicepparam
│   │
│   └── environments/                     # Environment overrides
│       ├── dev.bicepparam                # Development
│       ├── test.bicepparam               # Testing
│       ├── staging.bicepparam            # Staging
│       └── prod.bicepparam               # Production
│
└── config/
    └── guardrails/                       # YAML configs (easier to read)
        ├── content_filters.yaml
        ├── pii_filters.yaml
        └── environments.yaml
```

## Design Patterns

### Pattern 1: Modular Bicep Templates (Recommended)

**Separate concerns into focused modules**

#### Main RAI Policy Module
```bicep
// infrastructure/modules/guardrails/rai_policy.bicep
@description('Orchestrates all guardrail components')

param projectName string
param policyName string
param contentFilters array
param piiFilters array
param promptShields array
param tags object = {}

resource aiAccount 'Microsoft.CognitiveServices/accounts@2025-04-01-preview' existing = {
  name: projectName
}

resource raiPolicy 'Microsoft.CognitiveServices/accounts/raiPolicies@2025-04-01-preview' = {
  parent: aiAccount
  name: policyName
  properties: {
    mode: 'Default'
    basePolicyName: 'Microsoft.Default'
    contentFilters: contentFilters
    piiFilters: piiFilters
    promptShields: promptShields
  }
  tags: tags
}

output policyId string = raiPolicy.id
output policyName string = raiPolicy.name
```

#### Content Filters Module
```bicep
// infrastructure/modules/guardrails/content_filters.bicep
@description('Defines content filtering configurations')

param filterConfig object

output filters array = [
  {
    name: 'hate'
    enabled: filterConfig.hate.enabled
    severityThreshold: filterConfig.hate.severity
    blocking: filterConfig.hate.blocking
    source: 'Prompt'
  }
  {
    name: 'hate'
    enabled: filterConfig.hate.enabled
    severityThreshold: filterConfig.hate.severity
    blocking: filterConfig.hate.blocking
    source: 'Completion'
  }
  // ... repeat for sexual, violence, selfHarm
]
```

#### PII Filters Module
```bicep
// infrastructure/modules/guardrails/pii_filters.bicep
@description('Defines PII filtering configurations')

param piiConfig object

output filters array = [
  for category in items(piiConfig): {
    category: category.key
    mode: category.value.mode
    enabled: category.value.enabled
  }
]
```

### Pattern 2: Environment-Based Parameters

**Use inheritance: base config + environment overrides**

#### Base Configuration
```bicep
// infrastructure/parameters/base/content_filters_base.bicepparam
using '../../modules/guardrails/content_filters.bicep'

// Default settings for all environments
param filterConfig = {
  hate: {
    enabled: true
    severity: 'medium'
    blocking: true
  }
  sexual: {
    enabled: true
    severity: 'medium'
    blocking: true
  }
  violence: {
    enabled: true
    severity: 'medium'
    blocking: true
  }
  selfHarm: {
    enabled: true
    severity: 'high'
    blocking: true
  }
}
```

#### Environment-Specific Configuration
```bicep
// infrastructure/parameters/environments/prod.bicepparam
using '../../modules/guardrails/rai_policy.bicep'

// Import base configs
var baseContentFilters = loadJsonContent('../base/content_filters_base.json')
var basePiiFilters = loadJsonContent('../base/pii_filters_base.json')

param projectName = 'adusa-poc-agent-prod'
param policyName = 'prod-rai-policy'

// Override for production: stricter settings
param contentFilters = union(baseContentFilters, {
  hate: { severity: 'high' }      // Override: stricter in prod
  violence: { severity: 'high' }  // Override: stricter in prod
})

param piiFilters = union(basePiiFilters, {
  email: { mode: 'AnnotateAndBlock' }  // Override: block in prod
})

param tags = {
  environment: 'prod'
  criticality: 'high'
}
```

### Pattern 3: YAML Configuration with Conversion

**Use YAML for readability, convert to Bicep**

#### YAML Configuration
```yaml
# infrastructure/config/guardrails/environments.yaml
environments:
  dev:
    content_filters:
      hate: { severity: low, blocking: false }
      sexual: { severity: low, blocking: false }
      violence: { severity: low, blocking: false }
      selfHarm: { severity: medium, blocking: true }
    pii_filters:
      ssn: { mode: Annotate }
      creditCard: { mode: Annotate }
      email: { mode: Annotate }
  
  test:
    content_filters:
      hate: { severity: medium, blocking: true }
      sexual: { severity: medium, blocking: true }
      violence: { severity: medium, blocking: true }
      selfHarm: { severity: high, blocking: true }
    pii_filters:
      ssn: { mode: AnnotateAndBlock }
      creditCard: { mode: AnnotateAndBlock }
      email: { mode: Annotate }
  
  prod:
    content_filters:
      hate: { severity: high, blocking: true }
      sexual: { severity: high, blocking: true }
      violence: { severity: high, blocking: true }
      selfHarm: { severity: high, blocking: true }
    pii_filters:
      ssn: { mode: AnnotateAndBlock }
      creditCard: { mode: AnnotateAndBlock }
      email: { mode: AnnotateAndBlock }
      phoneNumber: { mode: AnnotateAndBlock }
```

#### Conversion Script
```python
# scripts/generate_guardrails_params.py
import yaml
import json
from pathlib import Path

def generate_bicep_params(environment: str):
    """Generate Bicep parameters from YAML config"""
    
    # Load YAML config
    config_file = Path('infrastructure/config/guardrails/environments.yaml')
    with open(config_file) as f:
        config = yaml.safe_load(f)
    
    env_config = config['environments'][environment]
    
    # Generate Bicep parameter file
    bicep_params = {
        'contentFilters': env_config['content_filters'],
        'piiFilters': env_config['pii_filters']
    }
    
    # Save as JSON (Bicep can load JSON)
    output_file = Path(f'infrastructure/parameters/environments/{environment}.json')
    with open(output_file, 'w') as f:
        json.dump(bicep_params, f, indent=2)
    
    print(f"✅ Generated {output_file}")

# Usage
generate_bicep_params('prod')
```

## Recommended Approach: Hybrid

**Combine the best of all patterns**

### Final Structure

```
infrastructure/
├── modules/guardrails/
│   ├── rai_policy.bicep              # Main orchestrator
│   ├── filters/                      # Filter definitions
│   │   ├── content.bicep
│   │   ├── pii.bicep
│   │   └── prompt_shield.bicep
│   └── presets/                      # Pre-built configs
│       ├── strict.bicep
│       ├── moderate.bicep
│       └── permissive.bicep
│
├── parameters/guardrails/
│   ├── base.bicepparam               # Shared defaults
│   ├── dev.bicepparam                # Dev overrides
│   ├── test.bicepparam               # Test overrides
│   ├── staging.bicepparam            # Staging overrides
│   └── prod.bicepparam               # Prod overrides
│
└── config/guardrails.yaml            # Human-readable config
```

### Implementation

#### 1. Base Configuration
```bicep
// infrastructure/parameters/guardrails/base.bicepparam
using '../modules/guardrails/rai_policy.bicep'

// Shared across all environments
param basePolicyName = 'Microsoft.Default'
param mode = 'Default'

// Default content filters
param defaultContentFilters = {
  hate: { enabled: true, severity: 'medium', blocking: true }
  sexual: { enabled: true, severity: 'medium', blocking: true }
  violence: { enabled: true, severity: 'medium', blocking: true }
  selfHarm: { enabled: true, severity: 'high', blocking: true }
}

// Default PII filters
param defaultPiiFilters = {
  ssn: { enabled: true, mode: 'AnnotateAndBlock' }
  creditCard: { enabled: true, mode: 'AnnotateAndBlock' }
  email: { enabled: true, mode: 'Annotate' }
}
```

#### 2. Environment-Specific Overrides
```bicep
// infrastructure/parameters/guardrails/prod.bicepparam
using '../modules/guardrails/rai_policy.bicep'

param projectName = 'adusa-poc-agent'
param policyName = 'prod-guardrails'

// Load base config
var base = loadJsonContent('./base.json')

// Override for production
param contentFilters = union(base.defaultContentFilters, {
  hate: { severity: 'high' }
  violence: { severity: 'high' }
})

param piiFilters = union(base.defaultPiiFilters, {
  email: { mode: 'AnnotateAndBlock' }
  phoneNumber: { enabled: true, mode: 'AnnotateAndBlock' }
})

param tags = {
  environment: 'prod'
  criticality: 'high'
  managedBy: 'devops'
}
```

#### 3. Deployment Script
```python
# scripts/deploy_guardrails.py
def deploy_guardrails(environment: str = 'dev'):
    """Deploy guardrails for specific environment"""
    
    param_file = f'infrastructure/parameters/guardrails/{environment}.bicepparam'
    
    if not Path(param_file).exists():
        raise FileNotFoundError(f"No config for environment: {environment}")
    
    # Deploy using Bicep
    subprocess.run([
        'az', 'deployment', 'group', 'create',
        '--resource-group', resource_group,
        '--template-file', 'infrastructure/modules/guardrails/rai_policy.bicep',
        '--parameters', param_file,
        '--name', f'guardrails-{environment}'
    ], check=True)
```

## Scaling Strategies

### Strategy 1: Filter Presets

**Create reusable preset configurations**

```bicep
// infrastructure/modules/guardrails/presets/strict.bicep
output contentFilters object = {
  hate: { enabled: true, severity: 'high', blocking: true }
  sexual: { enabled: true, severity: 'high', blocking: true }
  violence: { enabled: true, severity: 'high', blocking: true }
  selfHarm: { enabled: true, severity: 'high', blocking: true }
}

output piiFilters object = {
  ssn: { enabled: true, mode: 'AnnotateAndBlock' }
  creditCard: { enabled: true, mode: 'AnnotateAndBlock' }
  email: { enabled: true, mode: 'AnnotateAndBlock' }
  phoneNumber: { enabled: true, mode: 'AnnotateAndBlock' }
}
```

**Usage:**
```bicep
// Use preset
module strictPreset '../modules/guardrails/presets/strict.bicep'

param contentFilters = strictPreset.outputs.contentFilters
param piiFilters = strictPreset.outputs.piiFilters
```

### Strategy 2: Matrix Configuration

**Define all combinations in one place**

```yaml
# config/guardrails_matrix.yaml
filters:
  content:
    - name: hate
      dev: { severity: low, blocking: false }
      test: { severity: medium, blocking: true }
      prod: { severity: high, blocking: true }
    
    - name: sexual
      dev: { severity: low, blocking: false }
      test: { severity: medium, blocking: true }
      prod: { severity: high, blocking: true }
  
  pii:
    - category: ssn
      dev: { mode: Annotate }
      test: { mode: AnnotateAndBlock }
      prod: { mode: AnnotateAndBlock }
```

### Strategy 3: Composition

**Build complex policies from simple components**

```bicep
// Compose multiple filter modules
module contentFilters '../modules/guardrails/filters/content.bicep' = {
  name: 'content-filters'
  params: { config: contentFilterConfig }
}

module piiFilters '../modules/guardrails/filters/pii.bicep' = {
  name: 'pii-filters'
  params: { config: piiFilterConfig }
}

module promptShields '../modules/guardrails/filters/prompt_shield.bicep' = {
  name: 'prompt-shields'
  params: { config: promptShieldConfig }
}

// Combine into single policy
resource raiPolicy 'Microsoft.CognitiveServices/accounts/raiPolicies@2025-04-01-preview' = {
  properties: {
    contentFilters: contentFilters.outputs.filters
    piiFilters: piiFilters.outputs.filters
    promptShields: promptShields.outputs.shields
  }
}
```

## Deployment Workflow

### Multi-Environment Deployment

```bash
# Deploy to all environments
for env in dev test staging prod; do
  python3 scripts/deploy_guardrails.py $env
done

# Or use pipeline
az pipelines run \
  --name guardrails-pipeline \
  --parameters environment=prod
```

### Pipeline Configuration

```yaml
# pipelines/guardrails-pipeline.yml
parameters:
  - name: environment
    type: string
    values:
      - dev
      - test
      - staging
      - prod

stages:
  - stage: Deploy
    jobs:
      - job: DeployGuardrails
        steps:
          - script: |
              python3 scripts/deploy_guardrails.py ${{ parameters.environment }}
```

## Benefits

1. ✅ **Scalable**: Easy to add new filters
2. ✅ **Maintainable**: Clear separation of concerns
3. ✅ **Flexible**: Environment-specific overrides
4. ✅ **Reusable**: Shared base configurations
5. ✅ **Testable**: Each component can be tested independently
6. ✅ **Auditable**: Clear configuration history

## Migration Path

### Current → Recommended

```
Current:
infrastructure/parameters/guardrails.bicepparam

Recommended:
infrastructure/
├── parameters/guardrails/
│   ├── base.bicepparam
│   ├── dev.bicepparam
│   └── prod.bicepparam
```

### Migration Steps

1. Create `base.bicepparam` from current config
2. Create environment-specific files with overrides
3. Update deployment scripts
4. Test in dev
5. Roll out to other environments

## Next Steps

Would you like me to:
1. **Implement the recommended structure** for your project?
2. **Create the modular Bicep templates**?
3. **Set up environment-specific configurations**?
4. **Build the deployment automation**?
