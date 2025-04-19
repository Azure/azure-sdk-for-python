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
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${userassignedidentity.id}': {}
    }
  }
}

output AZURE_APPCONFIG_ID string = configurationstore.id
output AZURE_APPCONFIG_NAME string = configurationstore.name
output AZURE_APPCONFIG_RESOURCE_GROUP string = resourceGroup().name
output AZURE_APPCONFIG_ENDPOINT string = configurationstore.properties.endpoint


resource storageaccount_teststorage 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: 'teststorage'
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

output AZURE_STORAGE_ID_R string = storageaccount_teststorage.id
output AZURE_STORAGE_ID_STORAGE string = storageaccount_teststorage.id
output AZURE_STORAGE_NAME_R string = storageaccount_teststorage.name
output AZURE_STORAGE_NAME_STORAGE string = storageaccount_teststorage.name
output AZURE_STORAGE_RESOURCE_GROUP_R string = resourceGroup().name
output AZURE_STORAGE_RESOURCE_GROUP_STORAGE string = resourceGroup().name


resource blobservice_teststorage 'Microsoft.Storage/storageAccounts/blobServices@2024-01-01' = {
  parent: storageaccount_teststorage
  name: 'default'
}

output AZURE_BLOBS_ENDPOINT_R string = storageaccount_teststorage.properties.primaryEndpoints.blob
output AZURE_BLOBS_ENDPOINT_STORAGE string = storageaccount_teststorage.properties.primaryEndpoints.blob


resource container_teststorage 'Microsoft.Storage/storageAccounts/blobServices/containers@2022-09-01' = {
  parent: blobservice_teststorage
  name: defaultName
}

output AZURE_BLOB_CONTAINER_ID_R string = container_teststorage.id
output AZURE_BLOB_CONTAINER_NAME_R string = container_teststorage.name
output AZURE_BLOB_CONTAINER_RESOURCE_GROUP_R string = resourceGroup().name
output AZURE_BLOB_CONTAINER_ENDPOINT_R string = '${storageaccount_teststorage.properties.primaryEndpoints.blob}${container_teststorage.name}'


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
    value: storageaccount_teststorage.id
  }
}



resource keyvalue_azurestorageidstorage 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_STORAGE_ID_STORAGE'
  properties: {
    value: storageaccount_teststorage.id
  }
}



resource keyvalue_azurestoragenamer 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_STORAGE_NAME_R'
  properties: {
    value: storageaccount_teststorage.name
  }
}



resource keyvalue_azurestoragenamestorage 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_STORAGE_NAME_STORAGE'
  properties: {
    value: storageaccount_teststorage.name
  }
}



resource keyvalue_azurestorageresourcegroupr 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_STORAGE_RESOURCE_GROUP_R'
  properties: {
    value: resourceGroup().name
  }
}



resource keyvalue_azurestorageresourcegroupstorage 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_STORAGE_RESOURCE_GROUP_STORAGE'
  properties: {
    value: resourceGroup().name
  }
}



resource keyvalue_azureblobsendpointr 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_BLOBS_ENDPOINT_R'
  properties: {
    value: storageaccount_teststorage.properties.primaryEndpoints.blob
  }
}



resource keyvalue_azureblobsendpointstorage 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_BLOBS_ENDPOINT_STORAGE'
  properties: {
    value: storageaccount_teststorage.properties.primaryEndpoints.blob
  }
}



resource keyvalue_azureblobcontaineridr 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_BLOB_CONTAINER_ID_R'
  properties: {
    value: container_teststorage.id
  }
}



resource keyvalue_azureblobcontainernamer 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_BLOB_CONTAINER_NAME_R'
  properties: {
    value: container_teststorage.name
  }
}



resource keyvalue_azureblobcontainerresourcegroupr 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_BLOB_CONTAINER_RESOURCE_GROUP_R'
  properties: {
    value: resourceGroup().name
  }
}



resource keyvalue_azureblobcontainerendpointr 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_BLOB_CONTAINER_ENDPOINT_R'
  properties: {
    value: '${storageaccount_teststorage.properties.primaryEndpoints.blob}${container_teststorage.name}'
  }
}



resource roleassignment_gxaeyfznpvgorjrkpllp 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftAppConfigurationconfigurationStores', environmentName, defaultName, 'ServicePrincipal', 'App Configuration Data Reader')
  properties: {
    principalId: userassignedidentity.properties.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      '516239f1-63e1-4d78-a4de-a74fb236a071'
    )

  }
  scope: configurationstore
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



resource roleassignment_lyfnscmcgmmrvhbsjibc 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftStoragestorageAccountsblobServices', environmentName, storageaccount_teststorage.name, 'default', 'ServicePrincipal', 'Storage Blob Data Contributor')
  properties: {
    principalId: userassignedidentity.properties.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      'ba92f5b4-2d11-453d-a403-e96b0029c9fe'
    )

  }
  scope: blobservice_teststorage
}



resource roleassignment_oeildffbevchfgmsxfyk 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftStoragestorageAccountsblobServices', environmentName, storageaccount_teststorage.name, 'default', 'User', 'Storage Blob Data Contributor')
  properties: {
    principalId: principalId
    principalType: 'User'
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      'ba92f5b4-2d11-453d-a403-e96b0029c9fe'
    )

  }
  scope: blobservice_teststorage
}



resource roleassignment_babwvypdcuwfscunoiga 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftStoragestorageAccountsblobServicescontainers', environmentName, blobservice_teststorage.name, defaultName, 'ServicePrincipal', 'Storage Blob Data Contributor')
  properties: {
    principalId: userassignedidentity.properties.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      'ba92f5b4-2d11-453d-a403-e96b0029c9fe'
    )

  }
  scope: container_teststorage
}



resource roleassignment_xlzuvogwvgstrhiltzxm 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftStoragestorageAccountsblobServicescontainers', environmentName, blobservice_teststorage.name, defaultName, 'User', 'Storage Blob Data Contributor')
  properties: {
    principalId: principalId
    principalType: 'User'
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      'ba92f5b4-2d11-453d-a403-e96b0029c9fe'
    )

  }
  scope: container_teststorage
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



