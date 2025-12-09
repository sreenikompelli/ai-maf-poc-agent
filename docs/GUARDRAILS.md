# AI Foundry Guardrails

## Overview

Guardrails provide content filtering to ensure responsible AI by blocking harmful content across four categories: hate speech, sexual content, violence, and self-harm.

## Architecture

```
infrastructure/
├── modules/
│   └── guardrails/
│       └── content_filter.bicep    # Bicep template
├── parameters/
│   └── guardrails.bicepparam       # Configuration
└── README.md

scripts/
└── deploy_guardrails.py            # Deployment script

pipelines/
└── guardrails-pipeline.yml         # CI/CD pipeline
```

## Configuration

Edit `infrastructure/parameters/guardrails.bicepparam`:

```bicep
param contentFilterConfig = {
  hate: {
    enabled: true
    severity: 'medium'  // low, medium, or high
    blocking: true      // true = block, false = annotate
  }
  sexual: { enabled: true, severity: 'medium', blocking: true }
  violence: { enabled: true, severity: 'medium', blocking: true }
  selfHarm: { enabled: true, severity: 'high', blocking: true }
}
```

## Deployment

### Local
```bash
python3 scripts/deploy_guardrails.py nonprod
```

### CI/CD
Pipeline automatically deploys when changes are pushed to `main`:
- Triggers on changes to `infrastructure/modules/guardrails/**`
- Triggers on changes to `infrastructure/parameters/guardrails.bicepparam`

## Verification

```bash
# List deployed policies
az cognitiveservices account rai-policy list \
  --resource-group ad-usa-poc \
  --account-name adusa-poc-agent

# View in portal
# https://ai.azure.com → Project → Settings → Content Filters
```

## Severity Levels

| Level | Description | Use Case |
|-------|-------------|----------|
| `low` | Permissive | Testing |
| `medium` | Balanced | General use |
| `high` | Strict | Sensitive content |

## How It Works

```
User Input
    ↓
Content Filter (checks for harmful content)
    ↓
Agent Processing
    ↓
Content Filter (checks response)
    ↓
Response to User
```

## Adjusting Settings

1. Edit `infrastructure/parameters/guardrails.bicepparam`
2. Change severity levels or enable/disable categories
3. Redeploy: `python3 scripts/deploy_guardrails.py nonprod`

## Best Practices

- Always keep `selfHarm` at `high` severity
- Start with `medium` and adjust based on needs
- Use `blocking: false` for testing (annotate only)
- Monitor Application Insights for blocked requests

## Support

For issues, check the main project README or contact the platform team.
