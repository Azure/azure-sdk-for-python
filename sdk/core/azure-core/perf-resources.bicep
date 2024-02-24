param baseName string = resourceGroup().name
param location string = resourceGroup().location
param storageEndpointSuffix string = 'core.windows.net'
param testApplicationOid string

resource storageAccount 'Microsoft.Storage/storageAccounts@2019-06-01' = {
  name: '${baseName}storage'
  location: location
  kind: 'StorageV2'
  sku: {
    name: 'Standard_RAGRS'
  }
}

resource storageAccountBlobServices 'Microsoft.Storage/storageAccounts/blobServices@2021-09-01' = {
  name: 'default'
  parent: storageAccount
}

resource testContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2021-09-01' = {
  name: 'testcontainer'
  parent: storageAccountBlobServices

}

@description('This is the Blob owner role.')
resource blobOwnerRoleDefinition 'Microsoft.Authorization/roleDefinitions@2018-01-01-preview' existing = {
  scope: resourceGroup()
  name: 'b7e6dc6d-f1e8-4753-8033-0f276bb0955b'
}

resource blobRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(resourceGroup().id, testApplicationOid, blobOwnerRoleDefinition.id)
  properties: {
    roleDefinitionId: blobOwnerRoleDefinition.id
    principalId: testApplicationOid
    principalType: 'ServicePrincipal'
  }
}

resource tableServices 'Microsoft.Storage/storageAccounts/tableServices@2022-09-01' = {
  name: 'default'
  parent: storageAccount
}

resource tables 'Microsoft.Storage/storageAccounts/tableServices/tables@2022-09-01' = {
  name: 'default'
  parent: tableServices
}

@description('This is the Blob owner role.')
resource tableOwnerRoleDefinition 'Microsoft.Authorization/roleDefinitions@2018-01-01-preview' existing = {
  scope: resourceGroup()
  name: '0a9a7e1f-b9d0-4cc4-a60d-0319b160aaa3'
}

resource tableRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(resourceGroup().id, testApplicationOid, tableOwnerRoleDefinition.id)
  properties: {
    roleDefinitionId: tableOwnerRoleDefinition.id
    principalId: testApplicationOid
    principalType: 'ServicePrincipal'
  }
}

var storageAccountKey = storageAccount.listKeys('2021-09-01').keys[0].value
output AZURE_STORAGE_ACCOUNT_NAME string = storageAccount.name
output AZURE_STORAGE_BLOBS_ENDPOINT string = storageAccount.properties.primaryEndpoints.blob
output AZURE_STORAGE_ACCOUNT_KEY string = storageAccountKey
output AZURE_STORAGE_CONN_STR string = 'DefaultEndpointsProtocol=https;AccountName=${storageAccount.name};AccountKey=${storageAccountKey};EndpointSuffix=${storageEndpointSuffix}'
output AZURE_STORAGE_CONTAINER_NAME string = testContainer.name

output AZURE_STORAGE_TABLE_NAME string = tables.name
output AZURE_STORAGE_TABLES_ENDPOINT string = 'https://${storageAccount.name}.table.${storageEndpointSuffix}/'
