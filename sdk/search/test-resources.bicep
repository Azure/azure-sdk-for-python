
@description('The principal to assign the role to. This is application object id.')
param testApplicationOid string
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


resource searchService 'Microsoft.Search/searchServices@2024-03-01-preview' = {
  name: searchServiceName
  location: location // semantic search is available here
  sku: {
    name: searchSku
  }
  properties:  isPublicCloud ? {
    semanticSearch: 'standard'
    authOptions: {
      aadOrApiKey: {
        aadAuthFailureMode: 'http403'
      }
      apiKeyOnly: null
    }
  } : {}
}

resource searchServiceRoleAssignment 'Microsoft.Authorization/roleAssignments@2018-09-01-preview' = {  
  name: guid(resourceGroup().id, testApplicationOid, 'SearchServiceContributor')
  scope: resourceGroup()
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '7ca78c08-252a-4471-8644-bb5ff32d4ba0')
    principalId: testApplicationOid
    principalType: 'ServicePrincipal'
  }
}

resource searchIndexDataRoleAssignment 'Microsoft.Authorization/roleAssignments@2018-09-01-preview' = {  
  name: guid(resourceGroup().id, testApplicationOid, 'SearchIndexDataContributor')
  scope: resourceGroup()
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '8ebe5a00-799e-43f5-93ac-243d3dce84a7')
    principalId: testApplicationOid
    principalType: 'ServicePrincipal'
  }
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
output search_service_name string = searchServiceName
output search_storage_connection_string string = 'DefaultEndpointsProtocol=https;AccountName=${storageAccountName};AccountKey=${storageService.listKeys(storageApiVersion).keys[0].value};EndpointSuffix=${storageEndpointSuffix}'
output search_storage_container_name string = storageContainerName
output search_endpoint_suffix string = searchEndpointSuffix
