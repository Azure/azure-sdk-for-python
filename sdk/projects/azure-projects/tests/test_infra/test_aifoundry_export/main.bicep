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
output AZURE_AI_AISERVICES_ID_AI string = test_module.outputs.AZURE_AI_AISERVICES_ID_AI
output AZURE_AI_AISERVICES_NAME_AI string = test_module.outputs.AZURE_AI_AISERVICES_NAME_AI
output AZURE_AI_AISERVICES_RESOURCE_GROUP_AI string = test_module.outputs.AZURE_AI_AISERVICES_RESOURCE_GROUP_AI
output AZURE_AI_AISERVICES_ENDPOINT_AI string = test_module.outputs.AZURE_AI_AISERVICES_ENDPOINT_AI
output AZURE_SEARCH_ID_SEARCH string = test_module.outputs.AZURE_SEARCH_ID_SEARCH
output AZURE_SEARCH_NAME_SEARCH string = test_module.outputs.AZURE_SEARCH_NAME_SEARCH
output AZURE_SEARCH_RESOURCE_GROUP_SEARCH string = test_module.outputs.AZURE_SEARCH_RESOURCE_GROUP_SEARCH
output AZURE_SEARCH_ENDPOINT_SEARCH string = test_module.outputs.AZURE_SEARCH_ENDPOINT_SEARCH
output AZURE_STORAGE_ID_STORAGE string = test_module.outputs.AZURE_STORAGE_ID_STORAGE
output AZURE_STORAGE_NAME_STORAGE string = test_module.outputs.AZURE_STORAGE_NAME_STORAGE
output AZURE_STORAGE_RESOURCE_GROUP_STORAGE string = test_module.outputs.AZURE_STORAGE_RESOURCE_GROUP_STORAGE
output AZURE_BLOBS_ENDPOINT_STORAGE string = test_module.outputs.AZURE_BLOBS_ENDPOINT_STORAGE
output AZURE_KEYVAULT_ID_VAULT string = test_module.outputs.AZURE_KEYVAULT_ID_VAULT
output AZURE_KEYVAULT_NAME_VAULT string = test_module.outputs.AZURE_KEYVAULT_NAME_VAULT
output AZURE_KEYVAULT_RESOURCE_GROUP_VAULT string = test_module.outputs.AZURE_KEYVAULT_RESOURCE_GROUP_VAULT
output AZURE_KEYVAULT_ENDPOINT_VAULT string = test_module.outputs.AZURE_KEYVAULT_ENDPOINT_VAULT
output AZURE_AIFOUNDRY_HUB_ID_HUB string = test_module.outputs.AZURE_AIFOUNDRY_HUB_ID_HUB
output AZURE_AIFOUNDRY_HUB_NAME_HUB string = test_module.outputs.AZURE_AIFOUNDRY_HUB_NAME_HUB
output AZURE_AIFOUNDRY_HUB_RESOURCE_GROUP_HUB string = test_module.outputs.AZURE_AIFOUNDRY_HUB_RESOURCE_GROUP_HUB
output AZURE_AIFOUNDRY_PROJECT_ID_PROJECT string = test_module.outputs.AZURE_AIFOUNDRY_PROJECT_ID_PROJECT
output AZURE_AIFOUNDRY_PROJECT_NAME_PROJECT string = test_module.outputs.AZURE_AIFOUNDRY_PROJECT_NAME_PROJECT
output AZURE_AIFOUNDRY_PROJECT_RESOURCE_GROUP_PROJECT string = test_module.outputs.AZURE_AIFOUNDRY_PROJECT_RESOURCE_GROUP_PROJECT
output AZURE_AIFOUNDRY_PROJECT_ENDPOINT_PROJECT string = test_module.outputs.AZURE_AIFOUNDRY_PROJECT_ENDPOINT_PROJECT


