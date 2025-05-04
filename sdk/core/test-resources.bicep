@minLength(6)
@maxLength(21)
@description('The base resource name.')
param baseName string = resourceGroup().name

@description('Which Azure Region to deploy the resource to. Defaults to the resource group location.')
param location string = resourceGroup().location

@description('The client OID to grant access to test resources.')
param testApplicationOid string

// Storage Blob Data Contributor
var blobDataContributor = subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'ba92f5b4-2d11-453d-a403-e96b0029c9fe')

resource storageAccount 'Microsoft.Storage/storageAccounts@2022-09-01' = {
  name: '${baseName}sa'
  location: location
  kind: 'StorageV2'
  sku: {
    name: 'Standard_LRS'
  }
  properties: {
    accessTier: 'Hot'
  }
}

// Role assignment for the identity to access the storage account
resource storageRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(storageAccount.id, testApplicationOid, blobDataContributor)
  scope: storageAccount
  properties: {
    principalId: testApplicationOid
    roleDefinitionId: blobDataContributor
    principalType: 'ServicePrincipal'
  }
}

output AZURE_STORAGE_ACCOUNT_NAME string = storageAccount.name
output AZURE_STORAGE_BLOB_ENDPOINT string = storageAccount.properties.primaryEndpoints.blob
