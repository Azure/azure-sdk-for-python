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

param ValueA string

param ValueB string

param ValueC string

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
    ValueA: ValueA
    ValueB: ValueB
    ValueC: ValueC
  }
}
output AZURE_APPCONFIG_ID string = test_module.outputs.AZURE_APPCONFIG_ID
output AZURE_APPCONFIG_ID_A string = test_module.outputs.AZURE_APPCONFIG_ID_A
output AZURE_APPCONFIG_ID_B string = test_module.outputs.AZURE_APPCONFIG_ID_B
output AZURE_APPCONFIG_ID_C string = test_module.outputs.AZURE_APPCONFIG_ID_C
output AZURE_APPCONFIG_NAME string = test_module.outputs.AZURE_APPCONFIG_NAME
output AZURE_APPCONFIG_NAME_A string = test_module.outputs.AZURE_APPCONFIG_NAME_A
output AZURE_APPCONFIG_NAME_B string = test_module.outputs.AZURE_APPCONFIG_NAME_B
output AZURE_APPCONFIG_NAME_C string = test_module.outputs.AZURE_APPCONFIG_NAME_C
output AZURE_APPCONFIG_RESOURCE_GROUP string = test_module.outputs.AZURE_APPCONFIG_RESOURCE_GROUP
output AZURE_APPCONFIG_RESOURCE_GROUP_A string = test_module.outputs.AZURE_APPCONFIG_RESOURCE_GROUP_A
output AZURE_APPCONFIG_RESOURCE_GROUP_B string = test_module.outputs.AZURE_APPCONFIG_RESOURCE_GROUP_B
output AZURE_APPCONFIG_RESOURCE_GROUP_C string = test_module.outputs.AZURE_APPCONFIG_RESOURCE_GROUP_C
output AZURE_APPCONFIG_ENDPOINT string = test_module.outputs.AZURE_APPCONFIG_ENDPOINT
output AZURE_APPCONFIG_ENDPOINT_A string = test_module.outputs.AZURE_APPCONFIG_ENDPOINT_A
output AZURE_APPCONFIG_ENDPOINT_B string = test_module.outputs.AZURE_APPCONFIG_ENDPOINT_B
output AZURE_APPCONFIG_ENDPOINT_C string = test_module.outputs.AZURE_APPCONFIG_ENDPOINT_C


