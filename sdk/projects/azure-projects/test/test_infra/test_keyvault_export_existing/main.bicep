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

@sys.description('The Azure Active Directory tenant ID.')
param tenantId string = subscription().tenantId

@sys.description('Tags to apply to all resources in AZD envrionment.')
var azdTags = {
  'azd-env-name': environmentName
}

@sys.description('ID of the managed identity to assign application roles')
param managedIdentityId string = ''

@sys.description('Principal ID of the managed identity to assign application roles')
param managedIdentityPrincipalId string = ''

@sys.description('Client ID of the managed identity to assign application roles')
param managedIdentityClientId string = ''

resource resourcegroup_kvtest 'Microsoft.Resources/resourceGroups@2021-04-01' existing = {
  name: 'kvtest'
}

module test_module 'test.bicep' = {
  name: '${deployment().name}_test'
  scope: resourcegroup_kvtest
  params: {
    location: location
    environmentName: environmentName
    defaultNamePrefix: defaultNamePrefix
    defaultName: defaultName
    principalId: principalId
    tenantId: tenantId
    azdTags: azdTags
    managedIdentityId: managedIdentityId
    managedIdentityPrincipalId: managedIdentityPrincipalId
    managedIdentityClientId: managedIdentityClientId
  }
}
output AZURE_KEYVAULT_ID_KVTEST string = test_module.outputs.AZURE_KEYVAULT_ID_KVTEST
output AZURE_KEYVAULT_NAME_KVTEST string = test_module.outputs.AZURE_KEYVAULT_NAME_KVTEST
output AZURE_KEYVAULT_RESOURCE_GROUP_KVTEST string = test_module.outputs.AZURE_KEYVAULT_RESOURCE_GROUP_KVTEST
output AZURE_KEYVAULT_ENDPOINT_KVTEST string = test_module.outputs.AZURE_KEYVAULT_ENDPOINT_KVTEST


