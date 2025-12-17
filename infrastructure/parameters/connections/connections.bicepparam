// Connection Configuration for AI Foundry
// Maps to: infrastructure/modules/connections/connection.bicep

using '../../modules/connections/connection.bicep'

// Project Configuration
param accountName = 'adusa-poc-agent'
param projectName = 'adusa-poc-agent'

// Connection Settings
param connectionName = 'weathertool'
param targetUrl = 'https://wttr.in'
param openApiSpec = loadTextContent('./api.json')
param authType = 'CustomKeys'
param category = 'CustomKeys'
param apiKey = 'test'

// Tags
param tags = {
  environment: 'nonprod'
  managedBy: 'devops'
  project: 'ai-agents'
  module: 'connections'
}
