param baseName string = resourceGroup().name
param location string = resourceGroup().location

resource storageAccount 'Microsoft.Storage/storageAccounts@2019-06-01' = {
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

// .NET
output DATALAKE_STORAGE_ACCOUNT_NAME string = name
output DATALAKE_STORAGE_ACCOUNT_KEY string = key

// Java, JS
output STORAGE_CONNECTION_STRING string = connectionString

// Python
output AZURE_STORAGE_CONNECTION_STRING string = connectionString
