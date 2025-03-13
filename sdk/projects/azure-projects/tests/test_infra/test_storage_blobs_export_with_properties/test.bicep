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



resource storageaccount 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  properties: {
    accessTier: 'Hot'
    allowCrossTenantReplication: false
    allowSharedKeyAccess: false
  }
  name: defaultName
  location: location
  tags: azdTags
  kind: 'StorageV2'
  sku: {
    name: 'Standard_GRS'
  }
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${userassignedidentity.id}': {}
    }
  }
}

output AZURE_STORAGE_ID string = storageaccount.id
output AZURE_STORAGE_NAME string = storageaccount.name
output AZURE_STORAGE_RESOURCE_GROUP string = resourceGroup().name


resource blobservice 'Microsoft.Storage/storageAccounts/blobServices@2024-01-01' = {
  parent: storageaccount
  properties: {
    automaticSnapshotPolicyEnabled: true
    cors: {
      corsRules: [
        {
          allowedMethods: [
            'GET'
            'HEAD'
          ]
          maxAgeInSeconds: 5
        }
      ]
    }
    isVersioningEnabled: true
  }
  name: 'default'
}

output AZURE_BLOBS_ENDPOINT string = storageaccount.properties.primaryEndpoints.blob


resource roleassignment_encgtylpbtuphwxutrla 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftStoragestorageAccountsblobServices', 'default', 'ServicePrincipal', 'Storage Blob Data Contributor')
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



resource roleassignment_kucxlyfeelslmhoskuin 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftStoragestorageAccountsblobServices', 'default', 'User', 'Storage Blob Data Contributor')
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



