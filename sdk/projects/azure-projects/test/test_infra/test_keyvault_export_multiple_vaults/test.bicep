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



resource vault 'Microsoft.KeyVault/vaults@2024-12-01-preview' = {
  properties: {
    sku: {
      family: 'A'
      name: 'standard'
    }
    publicNetworkAccess: 'Enabled'
    tenantId: tenantId
    accessPolicies: []
    enableRbacAuthorization: true
  }
  name: defaultName
  location: location
  tags: azdTags
}

output AZURE_KEYVAULT_ID string = vault.id
output AZURE_KEYVAULT_NAME string = vault.name
output AZURE_KEYVAULT_RESOURCE_GROUP string = resourceGroup().name
output AZURE_KEYVAULT_ENDPOINT string = vault.properties.vaultUri


resource vault_foo 'Microsoft.KeyVault/vaults@2024-12-01-preview' = {
  properties: {
    sku: {
      family: 'A'
      name: 'standard'
    }
    publicNetworkAccess: 'Enabled'
    tenantId: tenantId
    accessPolicies: []
    enableRbacAuthorization: true
  }
  name: 'foo'
  location: location
  tags: azdTags
}

output AZURE_KEYVAULT_ID_FOO string = vault_foo.id
output AZURE_KEYVAULT_NAME_FOO string = vault_foo.name
output AZURE_KEYVAULT_RESOURCE_GROUP_FOO string = resourceGroup().name
output AZURE_KEYVAULT_ENDPOINT_FOO string = vault_foo.properties.vaultUri


resource roleassignment_qgdjhyhljucznkoutsgj 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftKeyVaultvaults', defaultName, 'ServicePrincipal', 'Key Vault Administrator')
  properties: {
    principalId: managedIdentityPrincipalId
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



resource roleassignment_rsoslitvdswlkijbvhek 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftKeyVaultvaults', 'foo', 'ServicePrincipal', 'Key Vault Administrator')
  properties: {
    principalId: managedIdentityPrincipalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      '00482a5a-887f-4fb3-b363-3b7fe8e74483'
    )

  }
  scope: vault_foo
}



resource roleassignment_nazfitmwnwmjfmzfvnkc 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftKeyVaultvaults', 'foo', 'User', 'Key Vault Administrator')
  properties: {
    principalId: principalId
    principalType: 'User'
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      '00482a5a-887f-4fb3-b363-3b7fe8e74483'
    )

  }
  scope: vault_foo
}



