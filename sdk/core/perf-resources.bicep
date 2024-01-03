param baseName string = resourceGroup().name
param location string = resourceGroup().location

resource storageAccount 'Microsoft.Storage/storageAccounts@2019-06-01' = {
  name: '${baseName}blob'
  location: location
  kind: 'BlockBlobStorage'
  sku: {
    name: 'Premium_LRS'
  }
}

resource storageAccountBlobServices 'Microsoft.Storage/storageAccounts/blobServices@2021-09-01' = {
  name: 'default'
  parent: storageAccount
}

resource testContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2021-09-01' = {
  name: 'testcontainer'
  parent: storageAccountBlobServices
  publicAccess: 'Container'

}

//param now string = utcNow()
//param expiryDate string = dateTimeAdd(now, 'P14D')
//param accountSasProperties object = {
//  signedServices: 'b'
//  signedPermission: 'rw'
//  signedExpiry: expiryDate
//  signedResourceTypes: 'sco'
//}
//
//var sasToken = storageAccount.listAccountSas('2021-09-01', accountSasProperties).accountSasToken

output AZURE_STORAGE_ACCOUNT_NAME string = storageAccount.name
output AZURE_STORAGE_ACCOUNT_ENDPOINT string = storageAccount.properties.primaryEndpoints.blob
output AZURE_STORAGE_ACCOUNT_KEY string = storageAccount.listKeys('2021-09-01').keys[0].value
//output AZURE_STORAGE_CONTAINER_URL string = containerUrl
output AZURE_STORAGE_CONTAINER_NAME string = testContainer.name
