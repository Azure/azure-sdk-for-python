targetScope = 'subscription'

@sys.description('Primary location for all resources')
@sys.minLength(1)
param location string

@sys.description('AZD environment name')
@sys.maxLength(64)
@sys.minLength(1)
param environmentName string

param defaultNamePrefix string = 'azproj'

param defaultName string = '${defaultNamePrefix}${uniqueString(subscription().subscriptionId, environmentName, location)}'

@sys.description('ID of the user or app to assign application roles')
param principalId string

@sys.secure()
@sys.description('The Azure Active Directory tenant ID.')
param tenantId string = subscription().tenantId

@sys.description('Tags to apply to all resources in AZD environment.')
var azdTags = {
  'azd-env-name': environmentName
}

resource resourcegroup 'Microsoft.Resources/resourceGroups@2021-04-01' = {
  name: defaultName
  location: location
  tags: azdTags
}

module test_module 'test.bicep' = {
  name: '${deployment().name}_test'
  scope: resourcegroup
  params: {
    location: location
    environmentName: environmentName
    defaultNamePrefix: defaultNamePrefix
    defaultName: defaultName
    principalId: principalId
    tenantId: tenantId
    azdTags: azdTags
  }
}
output AZURE_APPCONFIG_ID string = test_module.outputs.AZURE_APPCONFIG_ID
output AZURE_APPCONFIG_NAME string = test_module.outputs.AZURE_APPCONFIG_NAME
output AZURE_APPCONFIG_RESOURCE_GROUP string = test_module.outputs.AZURE_APPCONFIG_RESOURCE_GROUP
output AZURE_APPCONFIG_ENDPOINT string = test_module.outputs.AZURE_APPCONFIG_ENDPOINT
output AZURE_AI_AISERVICES_ID string = test_module.outputs.AZURE_AI_AISERVICES_ID
output AZURE_AI_AISERVICES_NAME string = test_module.outputs.AZURE_AI_AISERVICES_NAME
output AZURE_AI_AISERVICES_RESOURCE_GROUP string = test_module.outputs.AZURE_AI_AISERVICES_RESOURCE_GROUP
output AZURE_AI_AISERVICES_ENDPOINT string = test_module.outputs.AZURE_AI_AISERVICES_ENDPOINT
output AZURE_SEARCH_ID string = test_module.outputs.AZURE_SEARCH_ID
output AZURE_SEARCH_NAME string = test_module.outputs.AZURE_SEARCH_NAME
output AZURE_SEARCH_RESOURCE_GROUP string = test_module.outputs.AZURE_SEARCH_RESOURCE_GROUP
output AZURE_SEARCH_ENDPOINT string = test_module.outputs.AZURE_SEARCH_ENDPOINT
output AZURE_STORAGE_ID string = test_module.outputs.AZURE_STORAGE_ID
output AZURE_STORAGE_NAME string = test_module.outputs.AZURE_STORAGE_NAME
output AZURE_STORAGE_RESOURCE_GROUP string = test_module.outputs.AZURE_STORAGE_RESOURCE_GROUP
output AZURE_BLOBS_ENDPOINT string = test_module.outputs.AZURE_BLOBS_ENDPOINT
output AZURE_KEYVAULT_ID string = test_module.outputs.AZURE_KEYVAULT_ID
output AZURE_KEYVAULT_NAME string = test_module.outputs.AZURE_KEYVAULT_NAME
output AZURE_KEYVAULT_RESOURCE_GROUP string = test_module.outputs.AZURE_KEYVAULT_RESOURCE_GROUP
output AZURE_KEYVAULT_ENDPOINT string = test_module.outputs.AZURE_KEYVAULT_ENDPOINT
output AZURE_AIFOUNDRY_HUB_ID string = test_module.outputs.AZURE_AIFOUNDRY_HUB_ID
output AZURE_AIFOUNDRY_HUB_NAME string = test_module.outputs.AZURE_AIFOUNDRY_HUB_NAME
output AZURE_AIFOUNDRY_HUB_RESOURCE_GROUP string = test_module.outputs.AZURE_AIFOUNDRY_HUB_RESOURCE_GROUP
output AZURE_AIFOUNDRY_PROJECT_ID string = test_module.outputs.AZURE_AIFOUNDRY_PROJECT_ID
output AZURE_AIFOUNDRY_PROJECT_NAME string = test_module.outputs.AZURE_AIFOUNDRY_PROJECT_NAME
output AZURE_AIFOUNDRY_PROJECT_RESOURCE_GROUP string = test_module.outputs.AZURE_AIFOUNDRY_PROJECT_RESOURCE_GROUP
output AZURE_AIFOUNDRY_PROJECT_ENDPOINT string = test_module.outputs.AZURE_AIFOUNDRY_PROJECT_ENDPOINT


