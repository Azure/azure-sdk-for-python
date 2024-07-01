@description('The base resource name.')
param baseName string = resourceGroup().name


var location = resourceGroup().location
var authorizationRuleName_var = '${baseName}/RootManageSharedAccessKey'
var authorizationRuleNameNoManage_var = '${baseName}/NoManage'

var sbPremiumName = 'sb-premium-${baseName}'

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

resource servicebusPremium 'Microsoft.ServiceBus/namespaces@2018-01-01-preview' = {
  name: sbPremiumName
  location: location
  sku: {
    name: 'Premium'
    tier: 'Premium'
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

resource authorizationRuleNameNoManage 'Microsoft.ServiceBus/namespaces/AuthorizationRules@2015-08-01' = {
  name: authorizationRuleNameNoManage_var
  location: location
  properties: {
    rights: [
      'Listen'
      'Send'
    ]
  }
  dependsOn: [
    servicebus
  ]
}



resource testQueue 'Microsoft.ServiceBus/namespaces/queues@2017-04-01' = {
  parent: servicebus
  name: 'testQueue'
  properties: {
    lockDuration: 'PT5M'
    maxSizeInMegabytes: 1024
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

resource testQueueWithSessions 'Microsoft.ServiceBus/namespaces/queues@2017-04-01' = {
  parent: servicebus
  name: 'testQueueWithSessions'
  properties: {
    lockDuration: 'PT5M'
    maxSizeInMegabytes: 1024
    requiresDuplicateDetection: false
    requiresSession: true
    defaultMessageTimeToLive: 'P10675199DT2H48M5.4775807S'
    deadLetteringOnMessageExpiration: false
    duplicateDetectionHistoryTimeWindow: 'PT10M'
    maxDeliveryCount: 10
    autoDeleteOnIdle: 'P10675199DT2H48M5.4775807S'
    enablePartitioning: false
    enableExpress: false
  }
}


output SERVICE_BUS_FULLY_QUALIFIED_NAMESPACE string = replace(replace(servicebus.properties.serviceBusEndpoint, ':443/', ''), 'https://', '')
output QUEUE_NAME string = 'testQueue'
output QUEUE_NAME_WITH_SESSIONS string = 'testQueueWithSessions'
