param location string
param environmentName string
param defaultNamePrefix string
param defaultName string
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



resource storageaccount 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  properties: {
    accessTier: 'Hot'
    allowCrossTenantReplication: false
    allowSharedKeyAccess: false
  }
  name: defaultName
  location: location
  tags: azdTags
  kind: 'StorageV2'
  sku: {
    name: 'Standard_GRS'
  }
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${managedIdentityId}': {}
    }
  }
}

output AZURE_STORAGE_ID string = storageaccount.id
output AZURE_STORAGE_NAME string = storageaccount.name
output AZURE_STORAGE_RESOURCE_GROUP string = resourceGroup().name


resource tableservice 'Microsoft.Storage/storageAccounts/tableServices@2024-01-01' = {
  parent: storageaccount
  properties: {}
  name: 'default'
}

output AZURE_TABLES_ENDPOINT string = storageaccount.properties.primaryEndpoints.table


resource roleassignment_bamjaqdlyzrfpoiipogx 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftStoragestorageAccountstableServices', 'default', 'ServicePrincipal', 'Storage Table Data Owner')
  properties: {
    principalId: managedIdentityPrincipalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: 'Storage Table Data Owner'
  }
  scope: tableservice
}



