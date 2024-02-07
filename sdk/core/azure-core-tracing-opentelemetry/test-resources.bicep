@description('The base resource name.')
param baseName string = resourceGroup().name

@description('Which Azure Region to deploy the resource to. Defaults to the resource group location.')
param location string = resourceGroup().location

@description('The client OID to grant access to test resources.')
param testApplicationOid string

resource storageAccount 'Microsoft.Storage/storageAccounts@2022-09-01' = {
  name: '${baseName}storage'
  location: location
  kind: 'StorageV2'
  sku: {
    name: 'Standard_LRS'
  }
  properties: {
    accessTier: 'Hot'
  }
}

var name = storageAccount.name
var key = storageAccount.listKeys().keys[0].value
var connectionString = 'DefaultEndpointsProtocol=https;AccountName=${name};AccountKey=${key}'

output AZURE_STORAGE_ACCOUNT_NAME string = name
output AZURE_STORAGE_ACCOUNT_KEY string = key
output AZURE_STORAGE_CONNECTION_STRING string = connectionString
