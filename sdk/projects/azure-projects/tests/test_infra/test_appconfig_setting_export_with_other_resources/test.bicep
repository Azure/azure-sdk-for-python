param location string
param environmentName string
param defaultNamePrefix string
param defaultName string
param principalId string
param tenantId string
param azdTags object

resource userassignedidentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-07-31-preview' = {
  location: location
  tags: azdTags
  name: defaultName
}



resource configurationstore_testconfig 'Microsoft.AppConfiguration/configurationStores@2024-05-01' = {
  name: 'testconfig'
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
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${userassignedidentity.id}': {}
    }
  }
}

output AZURE_APPCONFIG_ID string = configurationstore_testconfig.id
output AZURE_APPCONFIG_ID_R string = configurationstore_testconfig.id
output AZURE_APPCONFIG_NAME string = configurationstore_testconfig.name
output AZURE_APPCONFIG_NAME_R string = configurationstore_testconfig.name
output AZURE_APPCONFIG_RESOURCE_GROUP string = resourceGroup().name
output AZURE_APPCONFIG_RESOURCE_GROUP_R string = resourceGroup().name
output AZURE_APPCONFIG_ENDPOINT string = configurationstore_testconfig.properties.endpoint
output AZURE_APPCONFIG_ENDPOINT_R string = configurationstore_testconfig.properties.endpoint


resource storageaccount 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: defaultName
  location: location
  tags: azdTags
  kind: 'StorageV2'
  sku: {
    name: 'Standard_GRS'
  }
  properties: {
    accessTier: 'Hot'
    allowCrossTenantReplication: false
    allowSharedKeyAccess: false
  }
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${userassignedidentity.id}': {}
    }
  }
}

output AZURE_STORAGE_ID_BLOBS string = storageaccount.id
output AZURE_STORAGE_NAME_BLOBS string = storageaccount.name
output AZURE_STORAGE_RESOURCE_GROUP_BLOBS string = resourceGroup().name


resource blobservice 'Microsoft.Storage/storageAccounts/blobServices@2024-01-01' = {
  parent: storageaccount
  name: 'default'
}

output AZURE_BLOBS_ENDPOINT_BLOBS string = storageaccount.properties.primaryEndpoints.blob


resource keyvalue_testconfigstore_foo 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore_testconfig
  name: 'foo'
  properties: {
    value: 'bar'
  }
}



resource keyvalue_testconfig_azureappconfigid 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore_testconfig
  name: 'AZURE_APPCONFIG_ID'
  properties: {
    value: configurationstore_testconfig.id
  }
}



resource keyvalue_testconfig_azureappconfigidr 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore_testconfig
  name: 'AZURE_APPCONFIG_ID_R'
  properties: {
    value: configurationstore_testconfig.id
  }
}



resource keyvalue_testconfig_azureappconfigname 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore_testconfig
  name: 'AZURE_APPCONFIG_NAME'
  properties: {
    value: configurationstore_testconfig.name
  }
}



resource keyvalue_testconfig_azureappconfignamer 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore_testconfig
  name: 'AZURE_APPCONFIG_NAME_R'
  properties: {
    value: configurationstore_testconfig.name
  }
}



resource keyvalue_testconfig_azureappconfigresourcegroup 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore_testconfig
  name: 'AZURE_APPCONFIG_RESOURCE_GROUP'
  properties: {
    value: resourceGroup().name
  }
}



resource keyvalue_testconfig_azureappconfigresourcegroupr 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore_testconfig
  name: 'AZURE_APPCONFIG_RESOURCE_GROUP_R'
  properties: {
    value: resourceGroup().name
  }
}



resource keyvalue_testconfig_azureappconfigendpoint 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore_testconfig
  name: 'AZURE_APPCONFIG_ENDPOINT'
  properties: {
    value: configurationstore_testconfig.properties.endpoint
  }
}



resource keyvalue_testconfig_azureappconfigendpointr 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore_testconfig
  name: 'AZURE_APPCONFIG_ENDPOINT_R'
  properties: {
    value: configurationstore_testconfig.properties.endpoint
  }
}



resource keyvalue_testconfig_azurestorageidblobs 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore_testconfig
  name: 'AZURE_STORAGE_ID_BLOBS'
  properties: {
    value: storageaccount.id
  }
}



resource keyvalue_testconfig_azurestoragenameblobs 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore_testconfig
  name: 'AZURE_STORAGE_NAME_BLOBS'
  properties: {
    value: storageaccount.name
  }
}



resource keyvalue_testconfig_azurestorageresourcegroupblobs 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore_testconfig
  name: 'AZURE_STORAGE_RESOURCE_GROUP_BLOBS'
  properties: {
    value: resourceGroup().name
  }
}



resource keyvalue_testconfig_azureblobsendpointblobs 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore_testconfig
  name: 'AZURE_BLOBS_ENDPOINT_BLOBS'
  properties: {
    value: storageaccount.properties.primaryEndpoints.blob
  }
}



resource roleassignment_qogxikugotebchvshxhg 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftAppConfigurationconfigurationStores', environmentName, 'testconfig', 'ServicePrincipal', 'App Configuration Data Reader')
  properties: {
    principalId: userassignedidentity.properties.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      '516239f1-63e1-4d78-a4de-a74fb236a071'
    )

  }
  scope: configurationstore_testconfig
}



resource roleassignment_xuveegsvkevnnlargjxd 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftAppConfigurationconfigurationStores', environmentName, 'testconfig', 'User', 'App Configuration Data Owner')
  properties: {
    principalId: principalId
    principalType: 'User'
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      '5ae67dd6-50cb-40e7-96ff-dc2bfa4b606b'
    )

  }
  scope: configurationstore_testconfig
}



resource roleassignment_qdxwvfwdcxdhyslfngyw 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftStoragestorageAccountsblobServices', environmentName, storageaccount.name, 'default', 'ServicePrincipal', 'Storage Blob Data Contributor')
  properties: {
    principalId: userassignedidentity.properties.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      'ba92f5b4-2d11-453d-a403-e96b0029c9fe'
    )

  }
  scope: blobservice
}



resource roleassignment_coargsxbrhdmojcevwkk 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftStoragestorageAccountsblobServices', environmentName, storageaccount.name, 'default', 'User', 'Storage Blob Data Contributor')
  properties: {
    principalId: principalId
    principalType: 'User'
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      'ba92f5b4-2d11-453d-a403-e96b0029c9fe'
    )

  }
  scope: blobservice
}



resource roleassignment_cjanxuzqqzqoebkzaspn 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftResourcesresourceGroups', environmentName, 'testconfig', 'User', 'App Configuration Data Owner')
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



