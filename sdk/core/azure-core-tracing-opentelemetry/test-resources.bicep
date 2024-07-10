@minLength(6)
@maxLength(21)
@description('The base resource name.')
param baseName string = resourceGroup().name

@description('Which Azure Region to deploy the resource to. Defaults to the resource group location.')
param location string = resourceGroup().location

@description('The client OID to grant access to test resources.')
param testApplicationOid string

var sbVersion = '2017-04-01'

resource storageAccount 'Microsoft.Storage/storageAccounts@2022-09-01' = {
  name: '${baseName}sa'
  location: location
  kind: 'StorageV2'
  sku: {
    name: 'Standard_LRS'
  }
  properties: {
    accessTier: 'Hot'
  }
}

resource serviceBusNamespace 'Microsoft.ServiceBus/namespaces@2017-04-01' = {
  name: '${baseName}sbnamespace'
  location: location
  sku: {
    name: 'Standard'
  }
  properties: {}
}

resource serviceBusQueue 'Microsoft.ServiceBus/namespaces/queues@2017-04-01' = {
  parent: serviceBusNamespace
  name: '${baseName}sbqueue'
  properties: {
    lockDuration: 'PT5M'
    maxSizeInMegabytes: 4096
    requiresDuplicateDetection: false
    requiresSession: false
    defaultMessageTimeToLive: 'P10675199DT2H48M5.4775807S'
    deadLetteringOnMessageExpiration: false
    duplicateDetectionHistoryTimeWindow: 'PT10M'
    maxDeliveryCount: 10
    autoDeleteOnIdle: 'P10675199DT2H48M5.4775807S'
    enablePartitioning: false
    enableExpress: false
  }
}

resource serviceBusTopic 'Microsoft.ServiceBus/namespaces/topics@2017-04-01' = {
  parent: serviceBusNamespace
  name: '${baseName}sbtopic'
  properties: {
    autoDeleteOnIdle: 'P10675199DT2H48M5.4775807S'
    defaultMessageTimeToLive: 'P10675199DT2H48M5.4775807S'
    duplicateDetectionHistoryTimeWindow: 'PT10M'
    enableBatchedOperations: true
    enableExpress: false
    enablePartitioning: false
    maxSizeInMegabytes: 4096
    requiresDuplicateDetection: false
    status: 'Active'
    supportOrdering: true
  }
}

resource serviceBusSubscription 'Microsoft.ServiceBus/namespaces/topics/subscriptions@2017-04-01' = {
  parent: serviceBusTopic
  name:  '${baseName}sbtopic'
  properties: {}
}

resource eventHubNamespace 'Microsoft.EventHub/namespaces@2021-11-01' = {
  name: '${baseName}eh'
  location: location
  sku: {
    capacity: 5
    name: 'Standard'
    tier: 'Standard'
  }

  resource eventHub 'eventhubs' = {
    name: 'eh-${baseName}-hub'
    properties: {
      partitionCount: 3
    }
  }
}

var authRuleResourceId = resourceId('Microsoft.ServiceBus/namespaces/authorizationRules', serviceBusNamespace.name, 'RootManageSharedAccessKey')
var eventHubsAuthRuleResourceId = resourceId('Microsoft.EventHub/namespaces/authorizationRules', eventHubNamespace.name, 'RootManageSharedAccessKey')

var name = storageAccount.name
var key = storageAccount.listKeys().keys[0].value
var storageConnectionString = 'DefaultEndpointsProtocol=https;AccountName=${name};AccountKey=${key}'
var serviceBusConnectionString = listkeys(authRuleResourceId, sbVersion).primaryConnectionString
var eventHubsConnectionString = listkeys(eventHubsAuthRuleResourceId, '2021-11-01').primaryConnectionString

output AZURE_STORAGE_ACCOUNT_NAME string = name
output AZURE_STORAGE_ACCOUNT_KEY string = key
output AZURE_STORAGE_CONNECTION_STRING string = storageConnectionString
output AZURE_SERVICEBUS_CONNECTION_STRING string = serviceBusConnectionString
output AZURE_SERVICEBUS_QUEUE_NAME string =  serviceBusQueue.name
output AZURE_SERVICEBUS_TOPIC_NAME string =  serviceBusTopic.name
output AZURE_SERVICEBUS_SUBSCRIPTION_NAME string =  serviceBusSubscription.name
output AZURE_EVENTHUB_CONNECTION_STRING string = eventHubsConnectionString
output AZURE_EVENTHUB_NAME string = eventHubNamespace::eventHub.name
