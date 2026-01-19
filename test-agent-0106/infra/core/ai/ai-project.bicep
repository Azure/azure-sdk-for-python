targetScope = 'resourceGroup'

@description('Tags that will be applied to all resources')
param tags object = {}

@description('Main location for the resources')
param location string

var resourceToken = uniqueString(subscription().id, resourceGroup().id, location)

@description('Name of the project')
param aiFoundryProjectName string

param deployments deploymentsType

@description('Id of the user or app to assign application roles')
param principalId string

@description('Principal type of user or app')
param principalType string

@description('Optional. Name of an existing AI Services account in the current resource group. If not provided, a new one will be created.')
param existingAiAccountName string = ''

@description('List of connections to provision')
param connections array = []

@description('Also provision dependent resources and connect to the project')
param additionalDependentResources dependentResourcesType

@description('Enable monitoring via appinsights and log analytics')
param enableMonitoring bool = true

@description('Enable hosted agent deployment')
param enableHostedAgents bool = false

// Load abbreviations
var abbrs = loadJsonContent('../../abbreviations.json')

// Determine which resources to create based on connections
var hasStorageConnection = length(filter(additionalDependentResources, conn => conn.resource == 'storage')) > 0
var hasAcrConnection = length(filter(additionalDependentResources, conn => conn.resource == 'registry')) > 0
var hasSearchConnection = length(filter(additionalDependentResources, conn => conn.resource == 'azure_ai_search')) > 0
var hasBingConnection = length(filter(additionalDependentResources, conn => conn.resource == 'bing_grounding')) > 0
var hasBingCustomConnection = length(filter(additionalDependentResources, conn => conn.resource == 'bing_custom_grounding')) > 0

// Extract connection names from ai.yaml for each resource type
var storageConnectionName = hasStorageConnection ? filter(additionalDependentResources, conn => conn.resource == 'storage')[0].connectionName : ''
var acrConnectionName = hasAcrConnection ? filter(additionalDependentResources, conn => conn.resource == 'registry')[0].connectionName : ''
var searchConnectionName = hasSearchConnection ? filter(additionalDependentResources, conn => conn.resource == 'azure_ai_search')[0].connectionName : ''
var bingConnectionName = hasBingConnection ? filter(additionalDependentResources, conn => conn.resource == 'bing_grounding')[0].connectionName : ''
var bingCustomConnectionName = hasBingCustomConnection ? filter(additionalDependentResources, conn => conn.resource == 'bing_custom_grounding')[0].connectionName : ''

// Enable monitoring via Log Analytics and Application Insights
module logAnalytics '../monitor/loganalytics.bicep' = if (enableMonitoring) {
  name: 'logAnalytics'
  params: {
    location: location
    tags: tags
    name: 'logs-${resourceToken}'
  }
}

module applicationInsights '../monitor/applicationinsights.bicep' = if (enableMonitoring) {
  name: 'applicationInsights'
  params: {
    location: location
    tags: tags
    name: 'appi-${resourceToken}'
    logAnalyticsWorkspaceId: logAnalytics.outputs.id
  }
}

// Always create a new AI Account for now (simplified approach)
// TODO: Add support for existing accounts in a future version
resource aiAccount 'Microsoft.CognitiveServices/accounts@2025-06-01' = {
  name: !empty(existingAiAccountName) ? existingAiAccountName : 'ai-account-${resourceToken}'
  location: location
  tags: tags
  sku: {
    name: 'S0'
  }
  kind: 'AIServices'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    allowProjectManagement: true
    customSubDomainName: !empty(existingAiAccountName) ? existingAiAccountName : 'ai-account-${resourceToken}'
    networkAcls: {
      defaultAction: 'Allow'
      virtualNetworkRules: []
      ipRules: []
    }
    publicNetworkAccess: 'Enabled'
    disableLocalAuth: true
  }
  
  @batchSize(1)
  resource seqDeployments 'deployments' = [
    for dep in (deployments??[]): {
      name: dep.name
      properties: {
        model: dep.model
      }
      sku: dep.sku
    }
  ]

  resource project 'projects' = {
    name: aiFoundryProjectName
    location: location
    identity: {
      type: 'SystemAssigned'
    }
    properties: {
      description: '${aiFoundryProjectName} Project'
      displayName: '${aiFoundryProjectName}Project'
    }
    dependsOn: [
      seqDeployments
    ]
  }

  resource aiFoundryAccountCapabilityHost 'capabilityHosts@2025-10-01-preview' = if (enableHostedAgents) {
    name: 'agents'
    properties: {
      capabilityHostKind: 'Agents'
      // IMPORTANT: this is required to enable hosted agents deployment
      // if no BYO Net is provided
      enablePublicHostingEnvironment: true
    }
  }
}


// Create connection towards appinsights
resource appInsightConnection 'Microsoft.CognitiveServices/accounts/projects/connections@2025-04-01-preview' = {
  parent: aiAccount::project
  name: 'appi-connection'
  properties: {
    category: 'AppInsights'
    target: applicationInsights.outputs.id
    authType: 'ApiKey'
    isSharedToAll: true
    credentials: {
      key: applicationInsights.outputs.connectionString
    }
    metadata: {
      ApiType: 'Azure'
      ResourceId: applicationInsights.outputs.id
    }
  }
}

// Create additional connections from ai.yaml configuration
module aiConnections './connection.bicep' = [for (connection, index) in connections: {
  name: 'connection-${connection.name}'
  params: {
    aiServicesAccountName: aiAccount.name
    aiProjectName: aiAccount::project.name
    connectionConfig: {
      name: connection.name
      category: connection.category
      target: connection.target
      authType: connection.authType
    }
    apiKey: '' // API keys should be provided via secure parameters or Key Vault
  }
}]

resource localUserAiDeveloperRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: resourceGroup()
  name: guid(subscription().id, resourceGroup().id, principalId, '64702f94-c441-49e6-a78b-ef80e0188fee')
  properties: {
    principalId: principalId
    principalType: principalType
    roleDefinitionId: resourceId('Microsoft.Authorization/roleDefinitions', '64702f94-c441-49e6-a78b-ef80e0188fee')
  }
}

resource localUserCognitiveServicesUserRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: resourceGroup()
  name: guid(subscription().id, resourceGroup().id, principalId, 'a97b65f3-24c7-4388-baec-2e87135dc908')
  properties: {
    principalId: principalId
    principalType: principalType
    roleDefinitionId: resourceId('Microsoft.Authorization/roleDefinitions', 'a97b65f3-24c7-4388-baec-2e87135dc908')
  }
}

resource projectCognitiveServicesUserRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: aiAccount
  name: guid(subscription().id, resourceGroup().id, aiAccount::project.name, '53ca6127-db72-4b80-b1b0-d745d6d5456d')
  properties: {
    principalId: aiAccount::project.identity.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: resourceId('Microsoft.Authorization/roleDefinitions', '53ca6127-db72-4b80-b1b0-d745d6d5456d')
  }
}


// All connections are now created directly within their respective resource modules
// using the centralized ./connection.bicep module

// Storage module - deploy if storage connection is defined in ai.yaml
module storage '../storage/storage.bicep' = if (hasStorageConnection) {
  name: 'storage'
  params: {
    location: location
    tags: tags
    resourceName: 'st${resourceToken}'
    connectionName: storageConnectionName
    principalId: principalId
    principalType: principalType
    aiServicesAccountName: aiAccount.name
    aiProjectName: aiAccount::project.name
  }
}

// Azure Container Registry module - deploy if ACR connection is defined in ai.yaml
module acr '../host/acr.bicep' = if (hasAcrConnection) {
  name: 'acr'
  params: {
    location: location
    tags: tags
    resourceName: '${abbrs.containerRegistryRegistries}${resourceToken}'
    connectionName: acrConnectionName
    principalId: principalId
    principalType: principalType
    aiServicesAccountName: aiAccount.name
    aiProjectName: aiAccount::project.name
  }
}

// Bing Search grounding module - deploy if Bing connection is defined in ai.yaml or parameter is enabled
module bingGrounding '../search/bing_grounding.bicep' = if (hasBingConnection) {
  name: 'bing-grounding'
  params: {
    tags: tags
    resourceName: 'bing-${resourceToken}'
    connectionName: bingConnectionName
    aiServicesAccountName: aiAccount.name
    aiProjectName: aiAccount::project.name
  }
}

// Bing Custom Search grounding module - deploy if custom Bing connection is defined in ai.yaml or parameter is enabled
module bingCustomGrounding '../search/bing_custom_grounding.bicep' = if (hasBingCustomConnection) {
  name: 'bing-custom-grounding'
  params: {
    tags: tags
    resourceName: 'bingcustom-${resourceToken}'
    connectionName: bingCustomConnectionName
    aiServicesAccountName: aiAccount.name
    aiProjectName: aiAccount::project.name
  }
}

// Azure AI Search module - deploy if search connection is defined in ai.yaml
module azureAiSearch '../search/azure_ai_search.bicep' = if (hasSearchConnection) {
  name: 'azure-ai-search'
  params: {
    tags: tags
    resourceName: 'search-${resourceToken}'
    connectionName: searchConnectionName
    storageAccountResourceId: hasStorageConnection ? storage!.outputs.storageAccountId : ''
    containerName: 'knowledge'
    aiServicesAccountName: aiAccount.name
    aiProjectName: aiAccount::project.name
    principalId: principalId
    principalType: principalType
    location: location
  }
}


// Outputs
output AZURE_AI_PROJECT_ENDPOINT string = aiAccount::project.properties.endpoints['AI Foundry API']
output AZURE_OPENAI_ENDPOINT string = aiAccount.properties.endpoints['OpenAI Language Model Instance API']
output aiServicesEndpoint string = aiAccount.properties.endpoint
output accountId string = aiAccount.id
output projectId string = aiAccount::project.id
output aiServicesAccountName string = aiAccount.name
output aiServicesProjectName string = aiAccount::project.name
output aiServicesPrincipalId string = aiAccount.identity.principalId
output projectName string = aiAccount::project.name
output APPLICATIONINSIGHTS_CONNECTION_STRING string = applicationInsights.outputs.connectionString

// Grouped dependent resources outputs
output dependentResources object = {
  registry: {
    name: hasAcrConnection ? acr!.outputs.containerRegistryName : ''
    loginServer: hasAcrConnection ? acr!.outputs.containerRegistryLoginServer : ''
    connectionName: hasAcrConnection ? acr!.outputs.containerRegistryConnectionName : ''
  }
  bing_grounding: {
    name: (hasBingConnection) ? bingGrounding!.outputs.bingGroundingName : ''
    connectionName: (hasBingConnection) ? bingGrounding!.outputs.bingGroundingConnectionName : ''
    connectionId: (hasBingConnection) ? bingGrounding!.outputs.bingGroundingConnectionId : ''
  }
  bing_custom_grounding: {
    name: (hasBingCustomConnection) ? bingCustomGrounding!.outputs.bingCustomGroundingName : ''
    connectionName: (hasBingCustomConnection) ? bingCustomGrounding!.outputs.bingCustomGroundingConnectionName : ''
    connectionId: (hasBingCustomConnection) ? bingCustomGrounding!.outputs.bingCustomGroundingConnectionId : ''
  }
  search: {
    serviceName: hasSearchConnection ? azureAiSearch!.outputs.searchServiceName : ''
    connectionName: hasSearchConnection ? azureAiSearch!.outputs.searchConnectionName : ''
  }
  storage: {
    accountName: hasStorageConnection ? storage!.outputs.storageAccountName : ''
    connectionName: hasStorageConnection ? storage!.outputs.storageConnectionName : ''
  }
}

type deploymentsType = {
  @description('Specify the name of cognitive service account deployment.')
  name: string

  @description('Required. Properties of Cognitive Services account deployment model.')
  model: {
    @description('Required. The name of Cognitive Services account deployment model.')
    name: string

    @description('Required. The format of Cognitive Services account deployment model.')
    format: string

    @description('Required. The version of Cognitive Services account deployment model.')
    version: string
  }

  @description('The resource model definition representing SKU.')
  sku: {
    @description('Required. The name of the resource model definition representing SKU.')
    name: string

    @description('The capacity of the resource model definition representing SKU.')
    capacity: int
  }
}[]?

type dependentResourcesType = {
  @description('The type of dependent resource to create')
  resource: 'storage' | 'registry' | 'azure_ai_search' | 'bing_grounding' | 'bing_custom_grounding'
  
  @description('The connection name for this resource')
  connectionName: string
}[]
