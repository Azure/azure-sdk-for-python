// cspell:ignore appi

targetScope = 'resourceGroup'

@description('The client object ID to grant access to the test resources.')
param testApplicationOid string

@minLength(6)
@maxLength(50)
@description('The base resource name.')
param baseName string = resourceGroup().name

@description('The Azure region for the Foundry project and telemetry resources.')
param location string = 'westus2'

@description('Whether to create the Foundry User and Monitoring Reader role assignments.')
param enableRoleAssignments bool = true

@description('The subscription that contains the qualified Agent Insights analysis model account.')
param analysisModelSubscriptionId string

@description('The resource group that contains the qualified Agent Insights analysis model account.')
param analysisModelResourceGroupName string

@description('The qualified Agent Insights analysis model account name.')
param analysisModelAccountName string

@description('The qualified Agent Insights analysis model deployment name.')
param analysisModelDeploymentName string = 'gpt-5.4'

@description('The qualified Agent Insights analysis model name.')
param analysisModelName string = 'gpt-5.4'

@description('The qualified Agent Insights analysis model version.')
param analysisModelVersion string = '2026-03-05'

@description('The qualified Agent Insights analysis model deployment SKU.')
param analysisModelSkuName string = 'GlobalStandard'

var foundryUserRoleId = subscriptionResourceId(
  'Microsoft.Authorization/roleDefinitions',
  '53ca6127-db72-4b80-b1b0-d745d6d5456d'
)
var monitoringReaderRoleId = subscriptionResourceId(
  'Microsoft.Authorization/roleDefinitions',
  '43d0d8ad-25c7-4714-9337-8ba259a9fe05'
)
var normalizedBaseName = toLower(
  replace(replace(replace(replace(baseName, '.', '-'), '_', '-'), '(', ''), ')', '')
)
var resourceSuffix = uniqueString(resourceGroup().id)
var aiServicesAccountName = take('${normalizedBaseName}-ai-${resourceSuffix}', 63)
var foundryProjectName = take('${normalizedBaseName}-project', 64)
var logAnalyticsWorkspaceName = take('${normalizedBaseName}-law-${resourceSuffix}', 63)
var applicationInsightsName = take('${normalizedBaseName}-appi-${resourceSuffix}', 260)
var fixtureAgentName = 'agent-insights-recording-${resourceSuffix}'
var fixtureOtelAgentId = '${fixtureAgentName}-otel-v1'
var applicationInsightsConnectionName = 'appinsights'
var analysisConnectionName = 'agent-insights-analysis'

resource analysisModelAccount 'Microsoft.CognitiveServices/accounts@2025-06-01' existing = {
  scope: resourceGroup(analysisModelSubscriptionId, analysisModelResourceGroupName)
  name: analysisModelAccountName
}

resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: logAnalyticsWorkspaceName
  location: location
  properties: {
    retentionInDays: 30
    features: {
      enableLogAccessUsingOnlyResourcePermissions: true
    }
    sku: {
      name: 'PerGB2018'
    }
  }
}

resource applicationInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: applicationInsightsName
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: logAnalytics.id
  }
}

resource aiServicesAccount 'Microsoft.CognitiveServices/accounts@2025-06-01' = {
  name: aiServicesAccountName
  location: location
  kind: 'AIServices'
  sku: {
    name: 'S0'
  }
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    allowProjectManagement: true
    customSubDomainName: aiServicesAccountName
    disableLocalAuth: true
    publicNetworkAccess: 'Enabled'
    networkAcls: {
      defaultAction: 'Allow'
      ipRules: []
      virtualNetworkRules: []
    }
  }
}

resource foundryProject 'Microsoft.CognitiveServices/accounts/projects@2025-06-01' = {
  parent: aiServicesAccount
  name: foundryProjectName
  location: location
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    displayName: foundryProjectName
    description: 'Temporary Azure SDK recording fixture for Agent Insights samples.'
  }
}

resource applicationInsightsConnection 'Microsoft.CognitiveServices/accounts/projects/connections@2025-04-01-preview' = {
  parent: foundryProject
  name: applicationInsightsConnectionName
  properties: {
    category: 'AppInsights'
    target: applicationInsights.id
    authType: 'ApiKey'
    isSharedToAll: true
    peRequirement: 'NotRequired'
    peStatus: 'NotApplicable'
    useWorkspaceManagedIdentity: false
    credentials: {
      key: applicationInsights.properties.ConnectionString
    }
    metadata: {
      ApiType: 'Azure'
      ResourceId: applicationInsights.id
    }
  }
}

resource analysisModelConnection 'Microsoft.CognitiveServices/accounts/projects/connections@2025-04-01-preview' = {
  parent: foundryProject
  name: analysisConnectionName
  properties: {
    category: 'ModelGateway'
    target: 'https://${analysisModelAccount.name}.openai.azure.com/openai/v1'
    authType: 'ApiKey'
    isSharedToAll: true
    peRequirement: 'NotRequired'
    peStatus: 'NotApplicable'
    useWorkspaceManagedIdentity: false
    credentials: {
      key: analysisModelAccount.listKeys().key1
    }
    metadata: {
      ApiType: 'Azure'
      ResourceId: analysisModelAccount.id
      location: analysisModelAccount.location
      deploymentInPath: 'false'
      models: string([
        {
          name: analysisModelDeploymentName
          sku: {
            name: analysisModelSkuName
          }
          capabilities: {
            chatCompletion: true
            responses: true
          }
          properties: {
            model: {
              name: analysisModelName
              version: analysisModelVersion
              format: 'OpenAI'
            }
          }
        }
      ])
    }
  }
}

resource capabilityHost 'Microsoft.CognitiveServices/accounts/capabilityHosts@2025-10-01-preview' = {
  parent: aiServicesAccount
  name: 'agents'
  properties: {
    capabilityHostKind: 'Agents'
    enablePublicHostingEnvironment: true
  }
  dependsOn: [
    foundryProject
  ]
}

resource testApplicationFoundryUser 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (enableRoleAssignments) {
  name: guid(aiServicesAccount.id, testApplicationOid, foundryUserRoleId)
  scope: aiServicesAccount
  properties: {
    roleDefinitionId: foundryUserRoleId
    principalId: testApplicationOid
  }
}

resource projectFoundryUser 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (enableRoleAssignments) {
  name: guid(aiServicesAccount.id, foundryProject.id, foundryUserRoleId)
  scope: aiServicesAccount
  properties: {
    roleDefinitionId: foundryUserRoleId
    principalId: foundryProject.identity.principalId
    principalType: 'ServicePrincipal'
  }
}

resource testApplicationMonitoringReader 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (enableRoleAssignments) {
  name: guid(applicationInsights.id, testApplicationOid, monitoringReaderRoleId)
  scope: applicationInsights
  properties: {
    roleDefinitionId: monitoringReaderRoleId
    principalId: testApplicationOid
  }
}

resource projectMonitoringReader 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (enableRoleAssignments) {
  name: guid(applicationInsights.id, foundryProject.id, monitoringReaderRoleId)
  scope: applicationInsights
  properties: {
    roleDefinitionId: monitoringReaderRoleId
    principalId: foundryProject.identity.principalId
    principalType: 'ServicePrincipal'
  }
}

output FOUNDRY_PROJECT_ENDPOINT string = foundryProject.properties.endpoints['AI Foundry API']
output FOUNDRY_AGENT_NAME string = fixtureAgentName
output FOUNDRY_MODEL_NAME string = '${analysisModelConnection.name}/${analysisModelDeploymentName}'
output LLM_VALIDATION_PROJECT_ENDPOINT string = foundryProject.properties.endpoints['AI Foundry API']
output LLM_VALIDATION_MODEL string = '${analysisModelConnection.name}/${analysisModelDeploymentName}'
output AGENT_INSIGHTS_OTEL_AGENT_ID string = fixtureOtelAgentId
output AGENT_INSIGHTS_APPLICATION_INSIGHTS_RESOURCE_ID string = applicationInsights.id
output AGENT_INSIGHTS_LOG_ANALYTICS_WORKSPACE_ID string = logAnalytics.id
output AGENT_INSIGHTS_PROJECT_RESOURCE_ID string = foundryProject.id
