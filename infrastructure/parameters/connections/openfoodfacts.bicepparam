// Connection Configuration for AI Foundry
// Maps to: infrastructure/modules/connections/connection.bicep

using '../../modules/connections/connection.bicep'

// Project Configuration
param projectName = 'adusa-poc-agent'

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
  managedBy: 'devops'
  project: 'ai-agents'
  module: 'connections'
}
