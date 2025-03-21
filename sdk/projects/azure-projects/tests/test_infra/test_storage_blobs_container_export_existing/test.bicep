param location string
param environmentName string
param defaultNamePrefix string
param defaultName string
param principalId string
param tenantId string
param azdTags object

resource configurationstore 'Microsoft.AppConfiguration/configurationStores@2024-05-01' = {
  properties: {
    disableLocalAuth: true
    createMode: 'Default'
    dataPlaneProxy: {
      authenticationMode: 'Pass-through'
      privateLinkDelegation: 'Disabled'
    }
    publicNetworkAccess: 'Enabled'
  }
  name: defaultName
  sku: {
    name: 'Standard'
  }
  location: location
  tags: azdTags
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${managedIdentityId}': {}
    }
  }
}

output AZURE_APPCONFIG_ID string = configurationstore.id
output AZURE_APPCONFIG_NAME string = configurationstore.name
output AZURE_APPCONFIG_RESOURCE_GROUP string = resourceGroup().name
output AZURE_APPCONFIG_ENDPOINT string = configurationstore.properties.endpoint


resource storageaccount_storagetest 'Microsoft.Storage/storageAccounts@2023-05-01' existing = {
  name: 'storagetest'
}

output AZURE_STORAGE_ID_STORAGETEST string = storageaccount_storagetest.id
output AZURE_STORAGE_NAME_STORAGETEST string = storageaccount_storagetest.name
output AZURE_STORAGE_RESOURCE_GROUP_STORAGETEST string = resourceGroup().name


resource blobservice_storagetest 'Microsoft.Storage/storageAccounts/blobServices@2024-01-01' existing = {
  name: 'default'
  parent: storageaccount_storagetest
}

output AZURE_BLOBS_ENDPOINT_STORAGETEST string = storageaccount_storagetest.properties.primaryEndpoints.blob


resource container_storagetest_test 'Microsoft.Storage/storageAccounts/blobServices/containers@2022-09-01' existing = {
  name: 'test'
  parent: blobservice_storagetest
}

output AZURE_BLOB_CONTAINER_ID_STORAGETEST_TEST string = container_storagetest_test.id
output AZURE_BLOB_CONTAINER_NAME_STORAGETEST_TEST string = container_storagetest_test.name
output AZURE_BLOB_CONTAINER_RESOURCE_GROUP_STORAGETEST_TEST string = resourceGroup().name
output AZURE_BLOB_CONTAINER_ENDPOINT_STORAGETEST_TEST string = '${storageaccount_storagetest.properties.primaryEndpoints.blob}${container_storagetest_test.name}'


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



resource keyvalue_azurestorageidstoragetest 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_STORAGE_ID_STORAGETEST'
  properties: {
    value: storageaccount_storagetest.id
  }
}



resource keyvalue_azurestoragenamestoragetest 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_STORAGE_NAME_STORAGETEST'
  properties: {
    value: storageaccount_storagetest.name
  }
}



resource keyvalue_azurestorageresourcegroupstoragetest 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_STORAGE_RESOURCE_GROUP_STORAGETEST'
  properties: {
    value: resourceGroup().name
  }
}



resource keyvalue_azureblobsendpointstoragetest 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_BLOBS_ENDPOINT_STORAGETEST'
  properties: {
    value: storageaccount_storagetest.properties.primaryEndpoints.blob
  }
}



resource keyvalue_azureblobcontaineridstoragetesttest 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_BLOB_CONTAINER_ID_STORAGETEST_TEST'
  properties: {
    value: container_storagetest_test.id
  }
}



resource keyvalue_azureblobcontainernamestoragetesttest 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_BLOB_CONTAINER_NAME_STORAGETEST_TEST'
  properties: {
    value: container_storagetest_test.name
  }
}



resource keyvalue_azureblobcontainerresourcegroupstoragetesttest 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_BLOB_CONTAINER_RESOURCE_GROUP_STORAGETEST_TEST'
  properties: {
    value: resourceGroup().name
  }
}



resource keyvalue_azureblobcontainerendpointstoragetesttest 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_BLOB_CONTAINER_ENDPOINT_STORAGETEST_TEST'
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
  scope: resourceGroup('rgtest')
}



