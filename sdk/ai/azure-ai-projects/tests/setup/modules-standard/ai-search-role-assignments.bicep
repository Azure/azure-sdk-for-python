// Assigns the necessary roles to the AI project

@description('Name of the AI Search resource')
param aiSearchName string

@description('Principal ID of the AI project')
param projectPrincipalId string

resource searchService 'Microsoft.Search/searchServices@2024-06-01-preview' existing = {
  name: aiSearchName
  scope: resourceGroup()
}

// search roles
resource searchIndexDataContributorRole 'Microsoft.Authorization/roleDefinitions@2022-04-01' existing = {
  name: '8ebe5a00-799e-43f5-93ac-243d3dce84a7'
  scope: resourceGroup()
}

resource searchIndexDataContributorAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: searchService
  name: guid(projectPrincipalId, searchIndexDataContributorRole.id, searchService.id)
  properties: {
    principalId: projectPrincipalId
    roleDefinitionId: searchIndexDataContributorRole.id
    principalType: 'ServicePrincipal'
  }
}

resource searchServiceContributorRole 'Microsoft.Authorization/roleDefinitions@2022-04-01' existing = {
  name: '7ca78c08-252a-4471-8644-bb5ff32d4ba0'
  scope: resourceGroup()
}

resource searchServiceContributorRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: searchService
  name: guid(projectPrincipalId, searchServiceContributorRole.id, searchService.id)
  properties: {
    principalId: projectPrincipalId
    roleDefinitionId: searchServiceContributorRole.id
    principalType: 'ServicePrincipal'
  }
}
