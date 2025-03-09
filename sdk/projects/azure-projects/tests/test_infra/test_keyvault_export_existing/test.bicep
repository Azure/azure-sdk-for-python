param location string
param environmentName string
param defaultNamePrefix string
param defaultName string
param principalId string
param tenantId string
param azdTags object
param managedIdentityId string
param managedIdentityPrincipalId string
param managedIdentityClientId string

resource vault_kvtest 'Microsoft.KeyVault/vaults@2024-12-01-preview' existing = {
  name: 'kvtest'
}

output AZURE_KEYVAULT_ID_KVTEST string = vault_kvtest.id
output AZURE_KEYVAULT_NAME_KVTEST string = vault_kvtest.name
output AZURE_KEYVAULT_RESOURCE_GROUP_KVTEST string = resourceGroup().name
output AZURE_KEYVAULT_ENDPOINT_KVTEST string = vault_kvtest.properties.vaultUri


