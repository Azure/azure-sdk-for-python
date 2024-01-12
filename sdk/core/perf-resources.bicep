param baseName string = resourceGroup().name
param location string = resourceGroup().location
param storageEndpointSuffix string = 'core.windows.net'

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

//resource storageTablesAccount 'Microsoft.Storage/storageAccounts@2022-09-01' = {
//  name: '${baseName}tables'
//  location: location
//  kind: 'StorageV2'
//  sku: {
//    name: 'Standard_RAGRS'
//  }
//}

resource tableServices 'Microsoft.Storage/storageAccounts/tableServices@2022-09-01' = {
  name: 'default'
  parent: storageAccount
}

resource tables 'Microsoft.Storage/storageAccounts/tableServices/tables@2022-09-01' = {
  name: 'default'
  parent: tableServices
}

var storageAccountKey = storageAccount.listKeys('2021-09-01').keys[0].value
output AZURE_STORAGE_ACCOUNT_NAME string = storageAccount.name
output AZURE_STORAGE_BLOBS_ENDPOINT string = storageAccount.properties.primaryEndpoints.blob
output AZURE_STORAGE_ACCOUNT_KEY string = storageAccountKey
output AZURE_STORAGE_CONN_STR string = 'DefaultEndpointsProtocol=https;AccountName=${storageAccount.name};AccountKey=${storageAccountKey};EndpointSuffix=${storageEndpointSuffix}'
output AZURE_STORAGE_CONTAINER_NAME string = testContainer.name
output AZURE_STORAGE_TABLE_NAME string = tables.name
output AZURE_STORAGE_TABLES_ENDPOINT string = '${storageAccount.name}.table.${storageEndpointSuffix}'

