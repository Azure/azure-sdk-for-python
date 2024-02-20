@description('The base resource name.')
param baseName string = resourceGroup().name

@description('Which Azure Region to deploy the resource to. Defaults to the resource group location.')
param location string = resourceGroup().location

@description('The principal to assign the role to. This is application object id.')
param testApplicationOid string

@description('Specifies the name of the Data Collection Endpoint to create.')
param dataCollectionEndpointName string = 'az-dce'

@description('Specifies the name of the Data Collection Rule to create.')
param dataCollectionRuleName string = 'az-dcr'

// Currently variables can't be used as keys, so the stream name is also hardcoded in the 'streamDeclarations' of the
// 'dataCollectionRules' resource below.
var streamName = 'Custom-MyTableRawData'
var tableName = 'MyTable_CL'

resource id 'Microsoft.Authorization/roleAssignments@2018-09-01-preview' = {
  name: guid(resourceGroup().id)
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '5ae67dd6-50cb-40e7-96ff-dc2bfa4b606b')
    principalId: testApplicationOid
  }
}

resource applicationInsightsComponent 'Microsoft.Insights/components@2020-02-02-preview' = {
  name: '${baseName}-appinsights-python'
  location: location
  kind: 'other'
  properties: {
    Application_Type: 'other'
    WorkspaceResourceId: primaryWorkspace.id
  }
}

resource dcrRoleAssignment 'Microsoft.Authorization/roleAssignments@2018-09-01-preview' = {
  name: guid(resourceGroup().id, dataCollectionRule.name, dataCollectionRule.id)
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '3913510d-42f4-4e42-8a64-420c390055eb')
    principalId: testApplicationOid
  }
}

resource dataCollectionEndpoint 'Microsoft.Insights/dataCollectionEndpoints@2021-04-01' = {
  name: dataCollectionEndpointName
  location: location
  properties: {
    networkAcls: {
      publicNetworkAccess: 'Enabled'
    }
  }
}

resource primaryWorkspace 'Microsoft.OperationalInsights/workspaces@2021-12-01-preview' = {
  name: '${baseName}-ws'
  location: location
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
    features: {
      enableLogAccessUsingOnlyResourcePermissions: true
    }
    workspaceCapping: {
      dailyQuotaGb: -1
    }
    publicNetworkAccessForIngestion: 'Enabled'
    publicNetworkAccessForQuery: 'Enabled'
  }

  resource workspaceTable 'tables' = {
    name: tableName
    properties: {
      totalRetentionInDays: 30
      plan: 'Analytics'
      schema: {
        name: tableName
        columns: [
          {
            name: 'TimeGenerated'
            type: 'datetime'
            description: 'The time at which the data was generated'
          }
          {
            name: 'AdditionalContext'
            type: 'dynamic'
            description: 'Additional message properties'
          }
          {
            name: 'ExtendedColumn'
            type: 'string'
            description: 'An additional column extended at ingestion time'
          }
        ]
      }
      retentionInDays: 30
    }
  }
}

resource secondaryWorkspace 'Microsoft.OperationalInsights/workspaces@2021-12-01-preview' = {
  name: '${baseName}-ws2'
  location: location
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
    features: {
      enableLogAccessUsingOnlyResourcePermissions: true
    }
    workspaceCapping: {
      dailyQuotaGb: -1
    }
    publicNetworkAccessForIngestion: 'Enabled'
    publicNetworkAccessForQuery: 'Enabled'
  }

  resource workspaceTable 'tables' = {
    name: tableName
    properties: {
      totalRetentionInDays: 30
      plan: 'Analytics'
      schema: {
        name: tableName
        columns: [
          {
            name: 'TimeGenerated'
            type: 'datetime'
            description: 'The time at which the data was generated'
          }
          {
            name: 'AdditionalContext'
            type: 'dynamic'
            description: 'Additional message properties'
          }
          {
            name: 'ExtendedColumn'
            type: 'string'
            description: 'An additional column extended at ingestion time'
          }
        ]
      }
      retentionInDays: 30
    }
  }
}

resource dataCollectionRule 'Microsoft.Insights/dataCollectionRules@2021-09-01-preview' = {
  name: dataCollectionRuleName
  location: location
  properties: {
    dataCollectionEndpointId: dataCollectionEndpoint.id
    streamDeclarations: {
      'Custom-MyTableRawData': {
        columns: [
          {
            name: 'Time'
            type: 'datetime'
          }
          {
            name: 'Computer'
            type: 'string'
          }
          {
            name: 'AdditionalContext'
            type: 'string'
          }
        ]
      }
      'Custom-MyTableRawData2': {
        columns: [
          {
            name: 'Time'
            type: 'datetime'
          }
          {
            name: 'Computer'
            type: 'string'
          }
          {
            name: 'AdditionalContext'
            type: 'string'
          }
        ]
      }
    }
    destinations: {
      logAnalytics: [
        {
          workspaceResourceId: primaryWorkspace.id
          name: primaryWorkspace.name
        }
        {
          workspaceResourceId: secondaryWorkspace.id
          name: secondaryWorkspace.name
        }
      ]
    }
    dataFlows: [
      {
        streams: [
          streamName
        ]
        destinations: [
          primaryWorkspace.name
        ]
        transformKql: 'source | extend jsonContext = parse_json(AdditionalContext) | project TimeGenerated = Time, Computer, AdditionalContext = jsonContext, ExtendedColumn=tostring(jsonContext.CounterName)'
        outputStream: 'Custom-${tableName}'
      }
      {
        streams: [
          '${streamName}2'
        ]
        destinations: [
          secondaryWorkspace.name
        ]
        transformKql: 'source | extend jsonContext = parse_json(AdditionalContext) | project TimeGenerated = Time, Computer, AdditionalContext = jsonContext, ExtendedColumn=tostring(jsonContext.CounterName)'
        outputStream: 'Custom-${tableName}'
      }
    ]
  }
  dependsOn: [
    primaryWorkspace::workspaceTable
    secondaryWorkspace::workspaceTable
  ]
}

output APPLICATIONINSIGHTS_CONNECTION_STRING string = applicationInsightsComponent.properties.ConnectionString
output METRICS_RESOURCE_ID string = applicationInsightsComponent.id
output AZURE_MONITOR_WORKSPACE_ID string = primaryWorkspace.properties.customerId
output AZURE_MONITOR_SECONDARY_WORKSPACE_ID string = secondaryWorkspace.properties.customerId
output AZURE_MONITOR_DCE string = dataCollectionEndpoint.properties.logsIngestion.endpoint
output AZURE_MONITOR_DCR_ID string = dataCollectionRule.properties.immutableId
output AZURE_MONITOR_STREAM_NAME string = streamName
output AZURE_MONITOR_TABLE_NAME string = tableName
