param isPublicCloud bool = environment().name == 'AzureCloud'
param searchEndpointSuffix string = 'search.windows.net'
param storageEndpointSuffix string = 'core.windows.net'
param location string = '${resourceGroup().location}'
param searchSku string = 'standard'
param searchServiceName string = 'search-${uniqueString(resourceGroup().id)}'
param searchApiVersion string = '2021-04-01-Preview'
param storageAccountName string = 'storage${uniqueString(resourceGroup().id)}'
param storageContainerName string = 'storage-container-${resourceGroup().name}'
param storageApiVersion string = '2021-06-01'


resource searchService 'Microsoft.Search/searchServices@2021-04-01-Preview' = {
  name: searchServiceName
  location: location // semantic search is available here
  sku: {
    name: searchSku
  }
  properties:  isPublicCloud ? {
    semanticSearch: 'standard'
  } : {}
}

resource storageService 'Microsoft.Storage/storageAccounts@2021-06-01' = {
  name: storageAccountName
  location: location
  sku: {
    /* cspell:disable-next-line */
    name: 'Standard_RAGRS'
  }
  kind: 'StorageV2'
  properties: {
    accessTier: 'Hot'
    supportsHttpsTrafficOnly: true
  }
}

resource container 'Microsoft.Storage/storageAccounts/blobServices/containers@2021-06-01' = {
  name: '${storageAccountName}/default/${storageContainerName}'
  dependsOn: [
    storageService
  ]
}

output search_service_endpoint string = 'https://${searchServiceName}.${searchEndpointSuffix}'
output search_service_api_key string = searchService.listAdminKeys(searchApiVersion).primaryKey
output search_query_api_key string = searchService.listQueryKeys(searchApiVersion).value[0].key
output search_service_name string = searchServiceName
output search_storage_connection_string string = 'DefaultEndpointsProtocol=https;AccountName=${storageAccountName};AccountKey=${storageService.listKeys(storageApiVersion).keys[0].value};EndpointSuffix=${storageEndpointSuffix}'
output search_storage_container_name string = storageContainerName
output search_endpoint_suffix string = searchEndpointSuffix