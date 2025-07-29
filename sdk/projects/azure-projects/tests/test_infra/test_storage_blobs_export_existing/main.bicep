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

resource resourcegroup_rgtest 'Microsoft.Resources/resourceGroups@2021-04-01' existing = {
  name: 'rgtest'
}

module test_module 'test.bicep' = {
  name: '${deployment().name}_test'
  scope: resourcegroup_rgtest
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
output AZURE_STORAGE_ID_R string = test_module.outputs.AZURE_STORAGE_ID_R
output AZURE_STORAGE_NAME_R string = test_module.outputs.AZURE_STORAGE_NAME_R
output AZURE_STORAGE_RESOURCE_GROUP_R string = test_module.outputs.AZURE_STORAGE_RESOURCE_GROUP_R
output AZURE_BLOBS_ENDPOINT_R string = test_module.outputs.AZURE_BLOBS_ENDPOINT_R


