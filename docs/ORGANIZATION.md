# Repository Organization

## Structure

```
ai-maf-poc-agent/
├── agents/                              # Agent definitions
│   └── weather-agent.yaml
│
├── infrastructure/                      # Infrastructure as Code
│   ├── modules/                         # Reusable Bicep modules
│   │   ├── connections/                 # Connection templates
│   │   │   ├── connection.bicep
│   │   │   └── api.json
│   │   └── guardrails/                  # Guardrails templates
│   │       └── content_filter.bicep
│   └── parameters/                      # Configuration files
│       ├── connections.bicepparam       # Connection settings
│       └── guardrails.bicepparam        # Guardrails settings
│
├── scripts/                             # Deployment scripts
│   ├── deploy_infrastructure.py         # Deploy connections
│   ├── deploy_agent.py                  # Deploy agents
│   ├── deploy_guardrails.py             # Deploy guardrails
│   └── tool_factory.py                  # Tool conversion logic
│
├── pipelines/                           # CI/CD pipelines
│   ├── infrastructure-pipeline.yml      # Connection deployment
│   ├── agent-pipeline.yml               # Agent deployment
│   └── guardrails-pipeline.yml          # Guardrails deployment
│
├── docs/                                # Documentation
│   └── GUARDRAILS.md                    # Guardrails guide
│
└── README.md                            # Main documentation
```

## Key Principles

### 1. Separation of Concerns
- **modules/**: Reusable Bicep templates (infrastructure code)
- **parameters/**: Configuration (data)
- **scripts/**: Deployment automation
- **pipelines/**: CI/CD workflows

### 2. No Environment Assumptions
- Configuration files don't assume specific environments
- Environment-specific values set via pipeline variables or command-line args
- Flexible for any deployment scenario

### 3. Single Source of Truth
- One README.md for main documentation
- One docs/GUARDRAILS.md for guardrails details
- No duplicate documentation

### 4. Enterprise-Friendly
- Clear folder structure
- Logical grouping
- Easy to navigate
- Scalable for future additions

## Configuration Files

### infrastructure/parameters/connections.bicepparam
Defines API connections for agents
- Project name
- Connection details
- OpenAPI specifications
- Tags

### infrastructure/parameters/guardrails.bicepparam
Defines content filtering policies
- Filter severity levels
- Enabled categories
- Blocking behavior
- Tags

## Adding New Components

### New Connection
1. Add OpenAPI spec to `infrastructure/modules/connections/`
2. Update `infrastructure/parameters/connections.bicepparam`
3. Deploy: `python scripts/deploy_infrastructure.py foundry_connection --bicepparam infrastructure/parameters/connections.bicepparam`

### New Guardrail Policy
1. Edit `infrastructure/parameters/guardrails.bicepparam`
2. Deploy: `python3 scripts/deploy_guardrails.py nonprod`

### New Agent
1. Create YAML in `agents/`
2. Deploy: `python -m scripts.deploy_agent <endpoint> agents/new-agent.yaml`

## Documentation

- **Main README**: Overview, quick start, deployment
- **docs/GUARDRAILS.md**: Detailed guardrails documentation
- **infrastructure/README.md**: Infrastructure-specific details

No duplicate or scattered documentation files.
