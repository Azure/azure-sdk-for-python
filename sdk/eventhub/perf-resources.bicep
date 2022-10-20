param baseName string = resourceGroup().name
param location string = resourceGroup().location

resource eventHubNamespace 'Microsoft.EventHub/namespaces@2015-08-01' = {
  name: 'eh-${baseName}'
  location: location
  sku: {
    capacity: 40
    name: 'Standard'
    tier: 'Standard'
  }

  resource eventHub 'eventhubs' = {
    name: 'eh-${baseName}-hub'
    properties: {
      partitionCount: 32
    }
  }
}

var eventHubsAuthRuleResourceId = resourceId('Microsoft.EventHub/namespaces/authorizationRules', eventHubNamespace.name, 'RootManageSharedAccessKey')

output AZURE_EVENTHUB_CONNECTION_STRING string = listkeys(eventHubsAuthRuleResourceId, '2015-08-01').primaryConnectionString
output AZURE_EVENTHUB_NAME string = eventHubNamespace::eventHub.name
