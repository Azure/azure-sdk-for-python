param location string
param environmentName string
param defaultNamePrefix string
param defaultName string
param principalId string
param tenantId string
param azdTags object

resource userassignedidentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-07-31-preview' = {
  location: location
  tags: azdTags
  name: defaultName
}



resource vault 'Microsoft.KeyVault/vaults@2024-12-01-preview' = {
  properties: {
    sku: {
      family: 'A'
      name: 'premium'
    }
    publicNetworkAccess: 'Disabled'
    tenantId: tenantId
    accessPolicies: []
    enableRbacAuthorization: true
  }
  location: 'westus'
  name: defaultName
  tags: azdTags
}

output AZURE_KEYVAULT_ID string = vault.id
output AZURE_KEYVAULT_NAME string = vault.name
output AZURE_KEYVAULT_RESOURCE_GROUP string = resourceGroup().name
output AZURE_KEYVAULT_ENDPOINT string = vault.properties.vaultUri


resource roleassignment_qgdjhyhljucznkoutsgj 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftKeyVaultvaults', defaultName, 'ServicePrincipal', 'Key Vault Administrator')
  properties: {
    principalId: userassignedidentity.properties.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      '00482a5a-887f-4fb3-b363-3b7fe8e74483'
    )

  }
  scope: vault
}



resource roleassignment_xotjgqfzvwectdhbwwhf 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftKeyVaultvaults', defaultName, 'User', 'Key Vault Administrator')
  properties: {
    principalId: principalId
    principalType: 'User'
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      '00482a5a-887f-4fb3-b363-3b7fe8e74483'
    )

  }
  scope: vault
}



