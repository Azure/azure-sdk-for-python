// Copyright (c) Microsoft Corporation. All rights reserved.
// Licensed under the MIT License.
//
// Provisions the Microsoft Foundry account/project used by the azure-ai-projects live Voice
// Agents realtime tests (tests/agents/test_voice_agent_realtime_livetest.py and its _async
// counterpart). See tests/README.md for details. The tests use a service-hosted realtime model
// (VoiceModelType.MANAGED), so no model deployment step is needed here.

@description('The client OID to grant Foundry User access to the test resources.')
param testApplicationOid string

@description('The base resource name.')
param baseName string = resourceGroup().name

@description('The location of the resource. By default, this is the same as the resource group.')
param location string = resourceGroup().location

var foundryAccountName = '${toLower(baseName)}-ai'
var foundryProjectName = '${toLower(baseName)}-project'
// Built-in "Foundry User" role -- lets the test principal create/manage voice agents in the project.
var foundryUserRoleId = subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '53ca6127-db72-4b80-b1b0-d745d6d5456d')

resource foundryAccount 'Microsoft.CognitiveServices/accounts@2025-04-01-preview' = {
  name: foundryAccountName
  location: location
  kind: 'AIServices'
  sku: {
    name: 'S0'
  }
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    customSubDomainName: toLower(foundryAccountName)
    allowProjectManagement: true
    defaultProjectName: foundryProjectName
    publicNetworkAccess: 'Enabled'
  }

  resource foundryProject 'projects' = {
    name: foundryProjectName
    location: location
    identity: {
      type: 'SystemAssigned'
    }
    sku: {
      name: 'S0'
    }
    properties: {
      displayName: foundryProjectName
      description: 'Foundry project used by the azure-ai-projects live voice-agents-realtime tests.'
    }
  }
}

resource foundryUserRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(resourceGroup().id, foundryAccount.id, foundryUserRoleId)
  scope: foundryAccount
  properties: {
    roleDefinitionId: foundryUserRoleId
    principalId: testApplicationOid
  }
}

// Outputs become environment variables injected into the test run.
output FOUNDRY_PROJECT_ENDPOINT string = '${foundryAccount.properties.endpoints['AI Foundry API']}api/projects/${foundryProjectName}'
output FOUNDRY_PROJECT_API_KEY string = foundryAccount.listKeys().key1
