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
    tenantId: tenantId
    azdTags: azdTags
  }
}
output AZURE_STORAGE_ID string = test_module.outputs.AZURE_STORAGE_ID
output AZURE_STORAGE_NAME string = test_module.outputs.AZURE_STORAGE_NAME
output AZURE_STORAGE_RESOURCE_GROUP string = test_module.outputs.AZURE_STORAGE_RESOURCE_GROUP
output AZURE_TABLES_ENDPOINT string = test_module.outputs.AZURE_TABLES_ENDPOINT


