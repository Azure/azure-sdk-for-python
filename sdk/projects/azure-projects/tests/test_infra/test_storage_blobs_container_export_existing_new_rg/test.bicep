param location string
param environmentName string
param defaultNamePrefix string
param defaultName string
param principalId string
param tenantId string
param azdTags object

resource configurationstore 'Microsoft.AppConfiguration/configurationStores@2024-05-01' = {
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
  tags: azdTags
}

output AZURE_APPCONFIG_ID string = configurationstore.id
output AZURE_APPCONFIG_NAME string = configurationstore.name
output AZURE_APPCONFIG_RESOURCE_GROUP string = resourceGroup().name
output AZURE_APPCONFIG_ENDPOINT string = configurationstore.properties.endpoint


resource resourcegroup_rgtest 'Microsoft.Resources/resourceGroups@2021-04-01' existing = {
  name: 'rgtest'
  scope: subscription()
}

resource storageaccount_storagetest 'Microsoft.Storage/storageAccounts@2023-05-01' existing = {
  name: 'storagetest'
  scope: resourcegroup_rgtest
}

output AZURE_STORAGE_ID_R string = storageaccount_storagetest.id
output AZURE_STORAGE_NAME_R string = storageaccount_storagetest.name
output AZURE_STORAGE_RESOURCE_GROUP_R string = 'rgtest'


resource blobservice_storagetest 'Microsoft.Storage/storageAccounts/blobServices@2024-01-01' existing = {
  name: 'default'
  parent: storageaccount_storagetest
}

output AZURE_BLOBS_ENDPOINT_R string = storageaccount_storagetest.properties.primaryEndpoints.blob


resource container_storagetest_test 'Microsoft.Storage/storageAccounts/blobServices/containers@2022-09-01' existing = {
  name: 'test'
  parent: blobservice_storagetest
}

output AZURE_BLOB_CONTAINER_ID_R string = container_storagetest_test.id
output AZURE_BLOB_CONTAINER_NAME_R string = container_storagetest_test.name
output AZURE_BLOB_CONTAINER_RESOURCE_GROUP_R string = 'rgtest'
output AZURE_BLOB_CONTAINER_ENDPOINT_R string = '${storageaccount_storagetest.properties.primaryEndpoints.blob}${container_storagetest_test.name}'


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



resource keyvalue_azurestorageidr 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_STORAGE_ID_R'
  properties: {
    value: storageaccount_storagetest.id
  }
}



resource keyvalue_azurestoragenamer 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_STORAGE_NAME_R'
  properties: {
    value: storageaccount_storagetest.name
  }
}



resource keyvalue_azurestorageresourcegroupr 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_STORAGE_RESOURCE_GROUP_R'
  properties: {
    value: 'rgtest'
  }
}



resource keyvalue_azureblobsendpointr 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_BLOBS_ENDPOINT_R'
  properties: {
    value: storageaccount_storagetest.properties.primaryEndpoints.blob
  }
}



resource keyvalue_azureblobcontaineridr 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_BLOB_CONTAINER_ID_R'
  properties: {
    value: container_storagetest_test.id
  }
}



resource keyvalue_azureblobcontainernamer 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_BLOB_CONTAINER_NAME_R'
  properties: {
    value: container_storagetest_test.name
  }
}



resource keyvalue_azureblobcontainerresourcegroupr 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_BLOB_CONTAINER_RESOURCE_GROUP_R'
  properties: {
    value: 'rgtest'
  }
}



resource keyvalue_azureblobcontainerendpointr 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_BLOB_CONTAINER_ENDPOINT_R'
  properties: {
    value: '${storageaccount_storagetest.properties.primaryEndpoints.blob}${container_storagetest_test.name}'
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



