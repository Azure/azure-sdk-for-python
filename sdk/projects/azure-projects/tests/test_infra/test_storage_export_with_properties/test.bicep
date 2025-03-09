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
    accessTier: 'Cool'
    allowCrossTenantReplication: true
    allowSharedKeyAccess: false
    isHnsEnabled: true
    allowBlobPublicAccess: true
    allowedCopyScope: 'PrivateLink'
    customDomain: {
      name: 'foo'
      useSubDomainName: true
    }
    defaultToOAuthAuthentication: true
    dnsEndpointType: 'AzureDnsZone'
    isNfsV3Enabled: true
    isSftpEnabled: true
    isLocalUserEnabled: false
    minimumTlsVersion: 'TLS1_3'
    networkAcls: {
      bypass: 'Metrics'
      defaultAction: 'Deny'
      resourceAccessRules: [
        {
          resourceId: 'foo'
        }
      ]
    }
    publicNetworkAccess: 'Enabled'
    sasPolicy: {
      sasExpirationPeriod: '30'
      expirationAction: 'Block'
    }
    supportsHttpsTrafficOnly: true
  }
  kind: 'BlobStorage'
  location: 'westus'
  identity: {
    type: 'SystemAssigned,UserAssigned'
    userAssignedIdentities: {
      identity: {}
    }
  }
  sku: {
    name: 'Premium_LRS'
  }
  tags: {
    foo: 'bar'
  }
  name: defaultName
}

output AZURE_STORAGE_ID string = storageaccount.id
output AZURE_STORAGE_NAME string = storageaccount.name
output AZURE_STORAGE_RESOURCE_GROUP string = resourceGroup().name


