@description('Name of the AI Foundry project')
param projectName string

@description('Name of the content filter')
param filterName string

@description('Content filter configuration for different categories')
param contentFilterConfig object = {
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
    severity: 'medium'
    blocking: true
  }
}

@description('Additional metadata tags')
param tags object = {}

// Reference to existing AI Foundry account (hub)
resource aiAccount 'Microsoft.CognitiveServices/accounts@2025-04-01-preview' existing = {
  name: projectName
}

// Create the content filter policy
resource contentFilter 'Microsoft.CognitiveServices/accounts/raiPolicies@2025-04-01-preview' = {
  parent: aiAccount
  name: filterName
  properties: {
    mode: 'Default'
    basePolicyName: 'Microsoft.Default'
    contentFilters: [
      {
        name: 'hate'
        enabled: contentFilterConfig.hate.enabled
        severityThreshold: contentFilterConfig.hate.severity
        blocking: contentFilterConfig.hate.blocking
        source: 'Prompt'
      }
      {
        name: 'hate'
        enabled: contentFilterConfig.hate.enabled
        severityThreshold: contentFilterConfig.hate.severity
        blocking: contentFilterConfig.hate.blocking
        source: 'Completion'
      }
      {
        name: 'sexual'
        enabled: contentFilterConfig.sexual.enabled
        severityThreshold: contentFilterConfig.sexual.severity
        blocking: contentFilterConfig.sexual.blocking
        source: 'Prompt'
      }
      {
        name: 'sexual'
        enabled: contentFilterConfig.sexual.enabled
        severityThreshold: contentFilterConfig.sexual.severity
        blocking: contentFilterConfig.sexual.blocking
        source: 'Completion'
      }
      {
        name: 'violence'
        enabled: contentFilterConfig.violence.enabled
        severityThreshold: contentFilterConfig.violence.severity
        blocking: contentFilterConfig.violence.blocking
        source: 'Prompt'
      }
      {
        name: 'violence'
        enabled: contentFilterConfig.violence.enabled
        severityThreshold: contentFilterConfig.violence.severity
        blocking: contentFilterConfig.violence.blocking
        source: 'Completion'
      }
      {
        name: 'self_harm'
        enabled: contentFilterConfig.selfHarm.enabled
        severityThreshold: contentFilterConfig.selfHarm.severity
        blocking: contentFilterConfig.selfHarm.blocking
        source: 'Prompt'
      }
      {
        name: 'self_harm'
        enabled: contentFilterConfig.selfHarm.enabled
        severityThreshold: contentFilterConfig.selfHarm.severity
        blocking: contentFilterConfig.selfHarm.blocking
        source: 'Completion'
      }
    ]
  }
  tags: union({
    deployedBy: 'bicep'
    purpose: 'content-filtering'
  }, tags)
}

// Outputs
output filterId string = contentFilter.id
output filterName string = contentFilter.name
output filterMode string = contentFilter.properties.mode
