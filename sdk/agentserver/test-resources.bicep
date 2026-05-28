@description('The base resource name.')
param baseName string = resourceGroup().name

@description('Which Azure Region to deploy the resource to. Defaults to the resource group location.')
param location string = resourceGroup().location

@description('The principal to assign the role to. This is application object id.')
param testApplicationOid string

// Monitoring Reader role definition ID
var monitoringReaderRoleId = subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '43d0d8ad-25c7-4714-9337-8ba259a9fe05')

resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: '${baseName}-appinsights'
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
  }
}

resource monitoringReaderRole 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(resourceGroup().id, testApplicationOid, monitoringReaderRoleId)
  properties: {
    roleDefinitionId: monitoringReaderRoleId
    principalId: testApplicationOid
    principalType: 'ServicePrincipal'
  }
}

output APPLICATIONINSIGHTS_CONNECTION_STRING string = appInsights.properties.ConnectionString
output APPLICATIONINSIGHTS_RESOURCE_ID string = appInsights.id
