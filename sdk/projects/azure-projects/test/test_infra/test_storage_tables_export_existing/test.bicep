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

resource storageaccount_storagetest 'Microsoft.Storage/storageAccounts@2023-05-01' existing = {
  name: 'storagetest'
}

output AZURE_STORAGE_ID_STORAGETEST string = storageaccount_storagetest.id
output AZURE_STORAGE_NAME_STORAGETEST string = storageaccount_storagetest.name
output AZURE_STORAGE_RESOURCE_GROUP_STORAGETEST string = resourceGroup().name


resource tableservice_storagetest 'Microsoft.Storage/storageAccounts/tableServices@2024-01-01' existing = {
  name: 'default'
  parent: storageaccount_storagetest
}

output AZURE_TABLES_ENDPOINT_STORAGETEST string = storageaccount_storagetest.properties.primaryEndpoints.table


