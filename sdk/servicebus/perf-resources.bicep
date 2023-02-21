@description('The base resource name.')
param baseName string = resourceGroup().name

@description('The client OID to grant access to test resources.')
param testApplicationOid string

var apiVersion = '2017-04-01'
var location = resourceGroup().location
var authorizationRuleName_var = '${baseName}/RootManageSharedAccessKey'

resource servicebus 'Microsoft.ServiceBus/namespaces@2018-01-01-preview' = {
  name: baseName
  location: location
  sku: {
    name: 'Standard'
    tier: 'Standard'
  }
  properties: {
    zoneRedundant: false
  }
}

resource authorizationRuleName 'Microsoft.ServiceBus/namespaces/AuthorizationRules@2015-08-01' = {
  name: authorizationRuleName_var
  location: location
  properties: {
    rights: [
      'Listen'
      'Manage'
      'Send'
    ]
  }
  dependsOn: [
    servicebus
  ]
}

output AZURE_SERVICEBUS_CONNECTION_STRING string = listKeys(resourceId('Microsoft.ServiceBus/namespaces/authorizationRules', baseName, 'RootManageSharedAccessKey'), apiVersion).primaryConnectionString
output AZURE_SERVICEBUS_ENDPOINT string = replace(servicebus.properties.serviceBusEndpoint, ':443/', '')
output testApplicationOid string = testApplicationOid
