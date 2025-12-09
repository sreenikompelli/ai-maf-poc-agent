// Guardrails Configuration
// Maps to: infrastructure/modules/guardrails/content_filter.bicep

using '../../modules/guardrails/content_filter.bicep'

// Project Configuration
param projectName = 'adusa-poc-agent'
param filterName = 'content-filter'

// Content Filter Configuration
param contentFilterConfig = {
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

// Tags
param tags = {
  environment: 'nonprod'
  managedBy: 'devops'
  project: 'ai-agents'
  purpose: 'content-filtering'
  module: 'guardrails'
}
