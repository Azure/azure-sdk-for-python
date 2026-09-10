// ============================================================================
// Azure AI Projects SDK Test Resources -- Voice Agent Live-Test Support
// ============================================================================
// This Bicep template provisions the Azure resources needed to run the
// live-only voice-agent realtime tests (tests/agents/test_voice_agent_realtime_live*.py)
// and to record/re-record the voice-agent conversation-read cassette
// (tests/agents/test_voice_agent_conversations*.py) against a real service.
//
// SCOPE NOTE: This intentionally covers only the voice-agent test surface, not
// the package's full recorded-test suite (datasets, evaluations, fine-tuning,
// memory search, etc.), which already runs entirely from committed cassettes
// and does not need a live resource. Provisioning a resource for that broader
// surface (additional model deployments, storage, connections, ...) is a
// separate, larger effort.
//
// Resources created:
//   1. Microsoft Foundry account (Microsoft.CognitiveServices/accounts, kind
//      AIServices, SKU S0) with a nested Foundry project.
//   2. Role assignment granting the test application the "Azure AI User" role
//      (matches the role this package's own samples/hosted_agents/rbac_util.py
//      uses for agent operations) -- authentication is Entra ID via
//      DefaultAzureCredential, no API keys.
//   3. A `gpt-realtime` model deployment, created separately by
//      test-resources-post.ps1 (deployments can take several minutes and this
//      lets the script retry/wait, which is awkward to express in Bicep).
//
// Outputs (become environment variables read by EnvironmentVariableLoader):
//   - FOUNDRY_PROJECT_ENDPOINT: the Foundry project endpoint, in the
//     `https://<account>.services.ai.azure.com/api/projects/<project>` form
//     these tests expect (see .env.template).
//   - FOUNDRY_VOICE_MODEL_NAME: the realtime model deployment name
//     (`gpt-realtime`), matching what test-resources-post.ps1 deploys.
// ============================================================================

@description('The client OID to grant access to test resources.')
param testApplicationOid string

@minLength(6)
@maxLength(50)
@description('The base resource name.')
param baseName string = resourceGroup().name

@description('The location of the resource. By default, this is the same as the resource group. gpt-realtime has restricted regional availability -- override this if the default region does not support it.')
param location string = resourceGroup().location

// Role definition ID for "Azure AI User" -- matches
// sdk/ai/azure-ai-projects/samples/hosted_agents/rbac_util.py's
// AZURE_AI_USER_ROLE_DEFINITION_GUID, the role this package's own samples use
// to grant an identity access to run agent operations against a Foundry
// project.
var azureAiUserRoleId = subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '53ca6127-db72-4b80-b1b0-d745d6d5456d')

// Resource names
var foundryAccountName = '${baseName}-voice-foundry'
var foundryProjectName = toLower(foundryAccountName)

// The Foundry account. `defaultProjectName`/the nested `projects` sub-resource
// below follow the same shape used by sdk/voicelive's test-resources.json.
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
    publicNetworkAccess: 'Enabled'
    allowProjectManagement: true
  }
}

resource foundryProject 'Microsoft.CognitiveServices/accounts/projects@2025-04-01-preview' = {
  parent: foundryAccount
  name: foundryProjectName
  location: location
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    displayName: foundryProjectName
    description: 'Voice agent live-test project for azure-ai-projects'
  }
}

// Grants the test application access to run agent/voice-agent operations.
// principalType is omitted so Azure can infer it (works for both a user and a
// service principal), matching the pattern used in
// sdk/contentunderstanding/test-resources.bicep.
resource testAppRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(resourceGroup().id, foundryAccount.id, azureAiUserRoleId)
  scope: foundryAccount
  properties: {
    roleDefinitionId: azureAiUserRoleId
    principalId: testApplicationOid
  }
}

// The gpt-realtime model deployment is created by test-resources-post.ps1
// after this template finishes deploying (see that script for why: model
// deployments can take several minutes and need retry/wait logic that's
// awkward to express here, following the same approach as
// sdk/contentunderstanding/test-resources.bicep).

output FOUNDRY_PROJECT_ENDPOINT string = 'https://${toLower(foundryAccountName)}.services.ai.azure.com/api/projects/${foundryProjectName}'
output FOUNDRY_VOICE_MODEL_NAME string = 'gpt-realtime'

// Additional outputs consumed by test-resources-post.ps1 to locate the
// account when deploying the model.
output FOUNDRY_VOICE_TEST_ACCOUNT_NAME string = foundryAccountName
output FOUNDRY_VOICE_TEST_RESOURCE_GROUP_NAME string = resourceGroup().name
