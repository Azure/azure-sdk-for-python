param baseName string

@description('Flag to enable or disable multiple write locations on CosmosDB Account')
param enableMultipleWriteLocations bool = false

@description('Default Cosmosdb Account level consistency')
param defaultConsistencyLevel string = 'Session'

@description('Enable multiple regions, default value is false')
param enableMultipleRegions bool = false

@description('Location for the Cosmos DB account.')
param location string = resourceGroup().location

@description('The api version to be used by Bicep to create resources')
param apiVersion string = '2023-04-15'

@description('The principal to assign the role to. This is application object id.')
param testApplicationOid string

var accountName = toLower(baseName)
var resourceId = cosmosAccount.id
var singleRegionConfiguration = [
  {
    locationName: 'East US 2'
    provisioningState: 'Succeeded'
    failoverPriority: 0
    isZoneRedundant: false
  }
]
var multiRegionConfiguration = [
  {
    locationName: 'West US 3'
    provisioningState: 'Succeeded'
    failoverPriority: 0
    isZoneRedundant: false
  }
  {
    locationName: 'West US'
    provisioningState: 'Succeeded'
    failoverPriority: 1
    isZoneRedundant: false
  }
]
var locationsConfiguration = (enableMultipleRegions ? multiRegionConfiguration : singleRegionConfiguration)
var roleDefinitionId = guid(baseName, 'roleDefinitionId')
var roleAssignmentId = guid(baseName, 'roleAssignmentId') 
var roleDefinitionName = 'ExpandedRbacActions'

resource cosmosAccount 'Microsoft.DocumentDB/databaseAccounts@2023-04-15' = {
  name: toLower(accountName)
  location: location
  kind: 'GlobalDocumentDB'
  properties: {
    publicNetworkAccess: 'Enabled'
    enableAutomaticFailover: false
    enableMultipleWriteLocations: enableMultipleWriteLocations
    isVirtualNetworkFilterEnabled: false
    disableKeyBasedMetadataWriteAccess: false
    enableFreeTier: false
    enableAnalyticalStorage: false
    databaseAccountOfferType: 'Standard'
    consistencyPolicy: {
      defaultConsistencyLevel: defaultConsistencyLevel
    }
    capabilities: [
        {name: 'EnableNoSQLVectorSearch'}, {name: 'EnableNoSQLFullTextSearch'}
    ]
    locations: locationsConfiguration
  }
}

resource accountName_roleDefinitionId 'Microsoft.DocumentDB/databaseAccounts/sqlRoleDefinitions@2023-04-15' = {
  parent: cosmosAccount 
  name: roleDefinitionId
  properties: {
    roleName: roleDefinitionName
    type: 'CustomRole'
    assignableScopes: [
      cosmosAccount.id 
    ]
    permissions: [
      {
        dataActions: [
          'Microsoft.DocumentDB/databaseAccounts/readMetadata'
          'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers/*'
          'Microsoft.DocumentDB/databaseAccounts/sqlDatabases/containers/items/*'
        ]
      }
    ]
  }
}

resource accountName_roleAssignmentId 'Microsoft.DocumentDB/databaseAccounts/sqlRoleAssignments@2023-04-15' = {
  parent: cosmosAccount 
  name: guid(resourceGroup().id, roleAssignmentId, testApplicationOid) 
  properties: {
    roleDefinitionId: accountName_roleDefinitionId.id
    principalId: testApplicationOid 
    scope: cosmosAccount.id
  }
}


output ACCOUNT_HOST string = reference(resourceId, apiVersion).documentEndpoint
output ACCOUNT_KEY string = listKeys(resourceId, apiVersion).primaryMasterKey
