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

param resourceGroupName string = 'bar'

resource resourcegroup_resourcegroupname 'Microsoft.Resources/resourceGroups@2021-04-01' = {
  name: resourceGroupName
  location: location
  tags: azdTags
}





