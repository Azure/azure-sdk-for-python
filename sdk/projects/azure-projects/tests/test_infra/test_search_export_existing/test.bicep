param location string
param environmentName string
param defaultNamePrefix string
param defaultName string
param principalId string
param tenantId string
param azdTags object

resource searchservice_test 'Microsoft.Search/searchServices@2024-06-01-Preview' existing = {
  name: 'test'
}

output AZURE_SEARCH_ID_TEST string = searchservice_test.id
output AZURE_SEARCH_NAME_TEST string = searchservice_test.name
output AZURE_SEARCH_RESOURCE_GROUP_TEST string = resourceGroup().name
output AZURE_SEARCH_ENDPOINT_TEST string = 'https://${searchservice_test.name}.search.windows.net/'


