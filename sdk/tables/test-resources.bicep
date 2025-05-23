@description('The base resource name.')
param baseName string

@description('The principal to assign the role to. This is application object id.')
param testApplicationOid string

@description('The url suffix to use when accessing the storage data plane.')
param storageEndpointSuffix string = 'core.windows.net'

@description('The url suffix to use when accessing the cosmos data plane.')
param cosmosEndpointSuffix string = 'cosmos.azure.com'

var location = resourceGroup().location
var primaryAccountName = '${replace(replace(baseName, '-', ''), '_', '')}prim'

var customCosmosRoleName = 'Azure Cosmos DB SDK role for Table Data Plane'

resource roleAssignment 'Microsoft.Authorization/roleAssignments@2018-09-01-preview' = {
  name: guid('tableDataContributorRoleId', resourceGroup().id)
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '0a9a7e1f-b9d0-4cc4-a60d-0319b160aaa3')
    principalId: testApplicationOid
  }
}

resource storageAccount 'Microsoft.Storage/storageAccounts@2023-05-01' = {
  name: primaryAccountName
  location: location
  sku: {
    name: 'Standard_RAGRS'
  }
  kind: 'StorageV2'
  properties: {
    networkAcls: {
      bypass: 'AzureServices'
      virtualNetworkRules: []
      ipRules: []
      defaultAction: 'Allow'
    }
    supportsHttpsTrafficOnly: true
    encryption: {
      services: {
        file: {
          enabled: true
        }
        blob: {
          enabled: true
        }
      }
      keySource: 'Microsoft.Storage'
    }
    accessTier: 'Cool'
    minimumTlsVersion: 'TLS1_2'
  }
}

resource cosmosAccount 'Microsoft.DocumentDB/databaseAccounts@2020-04-01' = {
  name: primaryAccountName
  location: location
  tags: {
    defaultExperience: 'Azure Table'
    CosmosAccountType: 'Non-Production'
  }
  kind: 'GlobalDocumentDB'
  properties: {
    enableAutomaticFailover: false
    enableMultipleWriteLocations: false
    isVirtualNetworkFilterEnabled: false
    virtualNetworkRules: []
    disableKeyBasedMetadataWriteAccess: false
    enableFreeTier: false
    enableAnalyticalStorage: false
    databaseAccountOfferType: 'Standard'
    consistencyPolicy: {
      defaultConsistencyLevel: 'BoundedStaleness'
      maxIntervalInSeconds: 86400
      maxStalenessPrefix: 1000000
    }
    locations: [
      {
        locationName: location
        failoverPriority: 0
        isZoneRedundant: false
      }
    ]
    capabilities: [
      {
        name: 'EnableTable'
      }
    ]
    ipRules: []
  }
}

resource cosmosRoleDef 'Microsoft.DocumentDB/databaseAccounts/tableRoleDefinitions@2024-12-01-preview' = {
  name: guid(customCosmosRoleName, 'roleDefinitionId')
  parent: cosmosAccount
  properties: {
    roleName: customCosmosRoleName
    permissions: [
      {
        dataActions: [
          'Microsoft.DocumentDB/databaseAccounts/readMetadata'
          'Microsoft.DocumentDB/databaseAccounts/tables/*'
          'Microsoft.DocumentDB/databaseAccounts/tables/containers/*'
          'Microsoft.DocumentDB/databaseAccounts/tables/containers/entities/*'
          'Microsoft.DocumentDB/databaseAccounts/throughputSettings/read'
        ]
      }
    ]
    assignableScopes: [
      cosmosAccount.id
    ]
  }
}

resource cosmosRoleAssignment 'Microsoft.DocumentDB/databaseAccounts/tableRoleAssignments@2024-12-01-preview' = {
  name: guid(customCosmosRoleName, 'roleAssignmentId')
  parent: cosmosAccount
  properties: {
    scope: cosmosAccount.id
    roleDefinitionId: cosmosRoleDef.id
    principalId: testApplicationOid
  }
}

output TABLES_STORAGE_ENDPOINT_SUFFIX string = storageEndpointSuffix
output TABLES_STORAGE_ACCOUNT_NAME string = primaryAccountName
output TABLES_PRIMARY_STORAGE_ACCOUNT_KEY string = storageAccount.listKeys().keys[0].value
output TABLES_COSMOS_ENDPOINT_SUFFIX string = cosmosEndpointSuffix
output TABLES_COSMOS_ACCOUNT_NAME string = primaryAccountName
output TABLES_PRIMARY_COSMOS_ACCOUNT_KEY string = cosmosAccount.listKeys().primaryMasterKey
