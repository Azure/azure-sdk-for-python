param location string
param environmentName string
param defaultNamePrefix string
param defaultName string
param principalId string
param tenantId string
param azdTags object
var managedIdentityId = userassignedidentity.id
var managedIdentityPrincipalId = userassignedidentity.properties.principalId
var managedIdentityClientId = userassignedidentity.properties.clientId

resource userassignedidentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-07-31-preview' = {
  location: location
  tags: azdTags
  name: defaultName
}



resource searchservice 'Microsoft.Search/searchServices@2024-06-01-Preview' = {
  properties: {
    publicNetworkAccess: 'Disabled'
  }
  name: defaultName
  sku: {
    name: 'basic'
  }
  location: location
  tags: azdTags
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${managedIdentityId}': {}
    }
  }
}

output AZURE_SEARCH_ID string = searchservice.id
output AZURE_SEARCH_NAME string = searchservice.name
output AZURE_SEARCH_RESOURCE_GROUP string = resourceGroup().name
output AZURE_SEARCH_ENDPOINT string = 'https://${searchservice.name}.search.windows.net/'


resource roleassignment_npmrnriktxggevypexnt 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftSearchsearchServices', defaultName, 'ServicePrincipal', 'Search Index Data Contributor')
  properties: {
    principalId: managedIdentityPrincipalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      '8ebe5a00-799e-43f5-93ac-243d3dce84a7'
    )

  }
  scope: searchservice
}



resource roleassignment_tcntafhtedyooituoovj 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftSearchsearchServices', defaultName, 'ServicePrincipal', 'Search Index Data Reader')
  properties: {
    principalId: managedIdentityPrincipalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      '1407120a-92aa-4202-b7e9-c0e197c71c8f'
    )

  }
  scope: searchservice
}



resource roleassignment_zcwvdaahcvxqfctejcey 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftSearchsearchServices', defaultName, 'ServicePrincipal', 'Search Service Contributor')
  properties: {
    principalId: managedIdentityPrincipalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      '7ca78c08-252a-4471-8644-bb5ff32d4ba0'
    )

  }
  scope: searchservice
}



resource roleassignment_qmbddeizydnvppopafhn 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftSearchsearchServices', defaultName, 'User', 'Search Index Data Contributor')
  properties: {
    principalId: principalId
    principalType: 'User'
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      '8ebe5a00-799e-43f5-93ac-243d3dce84a7'
    )

  }
  scope: searchservice
}



resource roleassignment_lwgbaxmwgckeacgtyitj 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftSearchsearchServices', defaultName, 'User', 'Search Index Data Reader')
  properties: {
    principalId: principalId
    principalType: 'User'
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      '1407120a-92aa-4202-b7e9-c0e197c71c8f'
    )

  }
  scope: searchservice
}



resource roleassignment_hanzilafpyksoxhwmdrt 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftSearchsearchServices', defaultName, 'User', 'Search Service Contributor')
  properties: {
    principalId: principalId
    principalType: 'User'
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      '7ca78c08-252a-4471-8644-bb5ff32d4ba0'
    )

  }
  scope: searchservice
}



