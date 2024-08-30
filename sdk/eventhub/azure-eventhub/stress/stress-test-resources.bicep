@description('The base resource name.')
param baseName string = resourceGroup().name

@description('The client OID to grant access to test resources.')
param testApplicationOid string

@description('The location of the resources. By default, this is the same as the resource group.')
param location string = resourceGroup().location

@description('The url suffix to use when creating storage connection strings.')
param storageEndpointSuffix string = 'core.windows.net'

var ehVersion = '2017-04-01'
var eventHubsNamespace_var = 'eh-${baseName}'
var eventHubName = 'eh-${baseName}-hub'
var eventHubAuthRuleName = 'eh-${baseName}-hub-auth-rule'
var storageAccount_var = replace('blb${baseName}', '-', '')
var containerName = 'your-blob-container-name'
var defaultSASKeyName = 'RootManageSharedAccessKey'
var eventHubsAuthRuleResourceId = resourceId('Microsoft.EventHub/namespaces/authorizationRules', eventHubsNamespace_var, defaultSASKeyName)
var storageAccountId = storageAccount.id

resource eventHubsNamespace 'Microsoft.EventHub/Namespaces@2017-04-01' = {
  name: eventHubsNamespace_var
  location: location
  sku: {
    name: 'Standard'
    tier: 'Standard'
  }
  properties: {}
}

resource eventHubsNamespace_eventHubName 'Microsoft.EventHub/namespaces/eventhubs@2017-04-01' = {
  name: '${eventHubsNamespace_var}/${eventHubName}'
  location: location
  properties: {
    messageRetentionInDays: 5
    partitionCount: 32
  }
  dependsOn: [
    eventHubsNamespace
  ]
}

resource eventHubsNamespace_eventHubName_eventHubAuthRuleName 'Microsoft.EventHub/namespaces/eventhubs/authorizationRules@2017-04-01' = {
  name: '${eventHubsNamespace_var}/${eventHubName}/${eventHubAuthRuleName}'
  properties: {
    rights: [
      'Manage'
      'Send'
      'Listen'
    ]
  }
  dependsOn: [
    eventHubsNamespace_eventHubName
  ]
}

resource storageAccount 'Microsoft.Storage/storageAccounts@2019-06-01' = {
  name: storageAccount_var
  location: location
  sku: {
    name: 'Standard_LRS'
    tier: 'Standard'
  }
  kind: 'StorageV2'
  properties: {
    accessTier: 'Hot'
  }
}

resource storageAccount_default_containerName 'Microsoft.Storage/storageAccounts/blobServices/containers@2019-06-01' = {
  name: '${storageAccount_var}/default/${containerName}'
  dependsOn: [
    storageAccount
  ]
}

output EVENT_HUB_NAMESPACE string = eventHubsNamespace_var
output EVENT_HUB_HOSTNAME string = '${eventHubsNamespace_var}.servicebus.windows.net'
output EVENT_HUB_NAME string = eventHubName
output EVENT_HUB_SAS_POLICY string = eventHubAuthRuleName
output EVENT_HUB_SAS_KEY string = listkeys(eventHubAuthRuleName, ehVersion).primaryKey
output AZURE_STORAGE_ACCOUNT string = storageAccount_var
output AZURE_STORAGE_ACCESS_KEY string = listKeys(storageAccountId, providers('Microsoft.Storage', 'storageAccounts').apiVersions[0]).keys[0].value
