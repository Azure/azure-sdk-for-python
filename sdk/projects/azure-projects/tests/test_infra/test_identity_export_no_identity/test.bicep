param location string
param environmentName string
param defaultNamePrefix string
param defaultName string
param principalId string
param tenantId string

resource configurationstore 'Microsoft.AppConfiguration/configurationStores@2024-05-01' = {
  tags: {
    'azd-env-name': environmentName
  }
  name: defaultName
  sku: {
    name: 'Standard'
  }
  properties: {
    disableLocalAuth: true
    createMode: 'Default'
    dataPlaneProxy: {
      authenticationMode: 'Pass-through'
      privateLinkDelegation: 'Disabled'
    }
    publicNetworkAccess: 'Enabled'
  }
  location: location
}

output AZURE_APPCONFIG_ID string = configurationstore.id
output AZURE_APPCONFIG_NAME string = configurationstore.name
output AZURE_APPCONFIG_RESOURCE_GROUP string = resourceGroup().name
output AZURE_APPCONFIG_ENDPOINT string = configurationstore.properties.endpoint


resource storageaccount_foo 'Microsoft.Storage/storageAccounts@2024-01-01' = {
  name: 'foo'
  tags: {
    'azd-env-name': environmentName
  }
  location: location
  kind: 'StorageV2'
  sku: {
    name: 'Standard_GRS'
  }
  properties: {
    accessTier: 'Hot'
    allowCrossTenantReplication: false
    allowSharedKeyAccess: false
  }
}

output AZURE_STORAGE_ID_STORAGE string = storageaccount_foo.id
output AZURE_STORAGE_NAME_STORAGE string = storageaccount_foo.name
output AZURE_STORAGE_RESOURCE_GROUP_STORAGE string = resourceGroup().name


resource keyvalue_azureappconfigid 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_APPCONFIG_ID'
  properties: {
    value: configurationstore.id
  }
}



resource keyvalue_azureappconfigname 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_APPCONFIG_NAME'
  properties: {
    value: configurationstore.name
  }
}



resource keyvalue_azureappconfigresourcegroup 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_APPCONFIG_RESOURCE_GROUP'
  properties: {
    value: resourceGroup().name
  }
}



resource keyvalue_azureappconfigendpoint 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_APPCONFIG_ENDPOINT'
  properties: {
    value: configurationstore.properties.endpoint
  }
}



resource keyvalue_azurestorageidstorage 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_STORAGE_ID_STORAGE'
  properties: {
    value: storageaccount_foo.id
  }
}



resource keyvalue_azurestoragenamestorage 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_STORAGE_NAME_STORAGE'
  properties: {
    value: storageaccount_foo.name
  }
}



resource keyvalue_azurestorageresourcegroupstorage 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_STORAGE_RESOURCE_GROUP_STORAGE'
  properties: {
    value: resourceGroup().name
  }
}



resource roleassignment_unxsuzdqhucrcsmcfuyc 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftAppConfigurationconfigurationStores', environmentName, defaultName, 'User', 'App Configuration Data Owner')
  properties: {
    principalId: principalId
    principalType: 'User'
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      '5ae67dd6-50cb-40e7-96ff-dc2bfa4b606b'
    )

  }
  scope: configurationstore
}



resource roleassignment_kvjoxlocbytxyhtrwdln 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftResourcesresourceGroups', environmentName, defaultName, 'User', 'App Configuration Data Owner')
  properties: {
    principalId: principalId
    principalType: 'User'
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      '5ae67dd6-50cb-40e7-96ff-dc2bfa4b606b'
    )

  }
  scope: resourceGroup()
}



