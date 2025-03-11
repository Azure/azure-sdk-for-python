param location string
param environmentName string
param defaultNamePrefix string
param defaultName string
param principalId string
param tenantId string
param azdTags object

resource configurationstore_test 'Microsoft.AppConfiguration/configurationStores@2024-05-01' existing = {
  name: 'test'
}

output AZURE_APPCONFIG_ID_TEST string = configurationstore_test.id
output AZURE_APPCONFIG_NAME_TEST string = configurationstore_test.name
output AZURE_APPCONFIG_RESOURCE_GROUP_TEST string = resourceGroup().name
output AZURE_APPCONFIG_ENDPOINT_TEST string = configurationstore_test.properties.endpoint


