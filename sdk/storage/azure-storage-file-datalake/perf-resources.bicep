param baseName string = resourceGroup().name
param location string = resourceGroup().location

resource storageAccount 'Microsoft.Storage/storageAccounts@2025-01-01' = {
  name: '${baseName}dlake'
  location: location
  kind: 'BlockBlobStorage'
  sku: {
    name: 'Premium_LRS'
  }
  properties: {
    isHnsEnabled: true
  }
}

var name = storageAccount.name
var key = storageAccount.listKeys().keys[0].value

// EndpointSuffix is required by azure-storage-file-datalake 12.7.0 and earlier (fixed in #24779)
var connectionString = 'DefaultEndpointsProtocol=https;AccountName=${name};AccountKey=${key};EndpointSuffix=core.windows.net'

output AZURE_STORAGE_CONNECTION_STRING string = connectionString
