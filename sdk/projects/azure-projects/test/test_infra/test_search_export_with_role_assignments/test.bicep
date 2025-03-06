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


resource roleassignment_qbbviszeosazsgwlhilc 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftSearchsearchServices', defaultName, 'ServicePrincipal', 'Contributor')
  properties: {
    principalId: managedIdentityPrincipalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      'b24988ac-6180-42a0-ab88-20f7382dd24c'
    )

  }
  scope: searchservice
}



resource roleassignment_jtcyeshddycdvariajfs 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftSearchsearchServices', defaultName, 'User', 'Contributor')
  properties: {
    principalId: principalId
    principalType: 'User'
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      'b24988ac-6180-42a0-ab88-20f7382dd24c'
    )

  }
  scope: searchservice
}



