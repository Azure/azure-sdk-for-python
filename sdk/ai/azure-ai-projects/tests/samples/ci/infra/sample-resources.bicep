// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

type ModelDeployment = {
  @minLength(1)
  name: string
  @minLength(1)
  version: string
  @minLength(1)
  sku: string
  @minValue(1)
  capacity: int
}

@minLength(2)
param accountName string
@minLength(2)
param projectName string
@minLength(36)
@maxLength(36)
param runnerPrincipalId string
@minLength(1)
param agentName string
param sampleModel ModelDeployment
param validationModel ModelDeployment
param provisionMcp bool = false

@secure()
@description('Complete GitHub PAT, including its prefix. Supplied only through an ADO secret.')
param mcpPat string = ''

resource account 'Microsoft.CognitiveServices/accounts@2025-10-01-preview' existing = {
  name: accountName
}

resource project 'Microsoft.CognitiveServices/accounts/projects@2025-10-01-preview' existing = {
  parent: account
  name: projectName
}

resource sampleDeployment 'Microsoft.CognitiveServices/accounts/deployments@2025-10-01-preview' = {
  parent: account
  name: sampleModel.name
  sku: {
    name: sampleModel.sku
    capacity: sampleModel.capacity
  }
  properties: {
    model: {
      format: 'OpenAI'
      name: sampleModel.name
      version: sampleModel.version
    }
    versionUpgradeOption: 'NoAutoUpgrade'
  }
}

// Console-output validation in the existing harness uses deployment gpt-5.2.
resource validationDeployment 'Microsoft.CognitiveServices/accounts/deployments@2025-10-01-preview' = if (sampleModel.name != validationModel.name) {
  parent: account
  name: validationModel.name
  sku: {
    name: validationModel.sku
    capacity: validationModel.capacity
  }
  properties: {
    model: {
      format: 'OpenAI'
      name: validationModel.name
      version: validationModel.version
    }
    versionUpgradeOption: 'NoAutoUpgrade'
  }
}

var foundryUserRole = subscriptionResourceId(
  'Microsoft.Authorization/roleDefinitions',
  '53ca6127-db72-4b80-b1b0-d745d6d5456d'
)
var openaiUserRole = subscriptionResourceId(
  'Microsoft.Authorization/roleDefinitions',
  '5e0bd9bd-7b93-4f28-af87-19fc36ad61bd'
)

resource runnerProjectAccess 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(project.id, runnerPrincipalId, foundryUserRole)
  scope: project
  properties: {
    principalId: runnerPrincipalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: foundryUserRole
  }
}

resource runnerModelAccess 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(account.id, runnerPrincipalId, openaiUserRole)
  scope: account
  properties: {
    principalId: runnerPrincipalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: openaiUserRole
  }
}

// Same contract as foundry-project-pool/provisions/provision-mcp-connection.ps1.
resource mcpConnection 'Microsoft.CognitiveServices/accounts/projects/connections@2025-10-01-preview' = if (provisionMcp) {
  parent: project
  name: 'mcp'
  properties: {
    category: 'RemoteTool'
    authType: 'CustomKeys'
    target: 'https://api.githubcopilot.com/mcp'
    isSharedToAll: false
    credentials: {
      keys: {
        Authorization: 'Bearer ${mcpPat}'
      }
    }
    metadata: {
      type: 'custom_MCP'
    }
  }
}

output environment object = {
  FOUNDRY_PROJECT_ENDPOINT: 'https://${accountName}.services.ai.azure.com/api/projects/${projectName}'
  FOUNDRY_MODEL_NAME: sampleDeployment.name
  FOUNDRY_AGENT_NAME: agentName
  LLM_VALIDATION_PROJECT_ENDPOINT: 'https://${accountName}.services.ai.azure.com/api/projects/${projectName}'
  MCP_PROJECT_CONNECTION_ID: provisionMcp ? mcpConnection!.id : ''
}
