param baseName string = resourceGroup().name
param location string = resourceGroup().location

var serviceBusNamespaceName = 'sb-${baseName}'
var serviceBusQueueName = '${serviceBusNamespaceName}-queue'
var serviceBusTopicName = '${serviceBusNamespaceName}-topic'
var serviceBusSubscriptionName = '${serviceBusNamespaceName}-subscription'
var defaultSASKeyName = 'RootManageSharedAccessKey'
var sbVersion = '2017-04-01'



resource serviceBusNamespace 'Microsoft.ServiceBus/namespaces@2017-04-01' = {
  name: serviceBusNamespaceName
  location: location
  sku: {
    name: 'Standard'
  }
  properties: {}
}

resource serviceBusQueue 'Microsoft.ServiceBus/namespaces/queues@2017-04-01' = {
  parent: serviceBusNamespace
  name: serviceBusQueueName
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
  name: serviceBusTopicName
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
  name: serviceBusSubscriptionName
  properties: {
  }
}

var authRuleResourceId = resourceId('Microsoft.ServiceBus/namespaces/authorizationRules', serviceBusNamespace.name, defaultSASKeyName)
output AZURE_SERVICEBUS_CONNECTION_STRING string = listkeys(authRuleResourceId, sbVersion).primaryConnectionString
output AZURE_SERVICEBUS_QUEUE_NAME string =  serviceBusQueue.name
output AZURE_SERVICEBUS_TOPIC_NAME string =  serviceBusTopic.name
output AZURE_SERVICEBUS_SUBSCRIPTION_NAME string =  serviceBusSubscription.name
