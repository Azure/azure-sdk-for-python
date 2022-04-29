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
param apiVersion string = '2020-04-01'

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
    locationName: 'East US 2'
    provisioningState: 'Succeeded'
    failoverPriority: 0
    isZoneRedundant: false
  }
  {
    locationName: 'East US'
    provisioningState: 'Succeeded'
    failoverPriority: 1
    isZoneRedundant: false
  }
]
var locationsConfiguration = (enableMultipleRegions ? multiRegionConfiguration : singleRegionConfiguration)

resource cosmosAccount 'Microsoft.DocumentDB/databaseAccounts@2020-04-01' = {
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
    locations: locationsConfiguration
  }
}


output ACCOUNT_HOST string = reference(resourceId, apiVersion).documentEndpoint
output ACCOUNT_KEY string = listKeys(resourceId, apiVersion).primaryMasterKey
