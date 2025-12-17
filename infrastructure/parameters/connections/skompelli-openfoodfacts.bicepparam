// Connection Configuration for AI Foundry - skompelli subscription
// Maps to: infrastructure/modules/connections/connection.bicep

using '../../modules/connections/connection.bicep'

// Project Configuration
param accountName = 'skompelli-agent-resource'
param projectName = 'skompelli-agent'

// Connection Settings
param connectionName = 'openfoodfacts'
param targetUrl = 'https://world.openfoodfacts.org'
param openApiSpec = loadTextContent('./openfoodfacts-api.json')
param authType = 'CustomKeys'
param category = 'CustomKeys'
param apiKey = 'test'

// Tags
param tags = {
  environment: 'nonprod'
  managedBy: 'cli'
  project: 'ai-agents'
  module: 'connections'
}
