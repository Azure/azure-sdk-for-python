// Assigns Role Cosmos DB Operator to the Project Principal ID
@description('Name of the AI Search resource')
param cosmosDBName string

@description('Principal ID of the AI project')
param projectPrincipalId string


resource cosmosDBAccount 'Microsoft.DocumentDB/databaseAccounts@2024-12-01-preview' existing = {
  name: cosmosDBName
  scope: resourceGroup()
}

resource cosmosDBOperatorRole 'Microsoft.Authorization/roleDefinitions@2022-04-01' existing = {
  name: '230815da-be43-4aae-9cb4-875f7bd000aa'
  scope: resourceGroup()
}

resource cosmosDBOperatorRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: cosmosDBAccount
  name: guid(projectPrincipalId, cosmosDBOperatorRole.id, cosmosDBAccount.id)
  properties: {
    principalId: projectPrincipalId
    roleDefinitionId: cosmosDBOperatorRole.id
    principalType: 'ServicePrincipal'
  }
}
