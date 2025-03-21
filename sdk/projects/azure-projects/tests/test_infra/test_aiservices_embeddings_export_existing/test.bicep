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


resource aiservices_account_aitest 'Microsoft.CognitiveServices/accounts@2024-10-01' existing = {
  name: 'aitest'
}

output AZURE_AI_AISERVICES_ID_AITEST string = aiservices_account_aitest.id
output AZURE_AI_AISERVICES_NAME_AITEST string = aiservices_account_aitest.name
output AZURE_AI_AISERVICES_RESOURCE_GROUP_AITEST string = resourceGroup().name
output AZURE_AI_AISERVICES_ENDPOINT_AITEST string = aiservices_account_aitest.properties.endpoint


resource embeddings_deployment_aitest_aitest 'Microsoft.CognitiveServices/accounts/deployments@2024-10-01' existing = {
  name: 'aitest'
  parent: aiservices_account_aitest
}

output AZURE_AI_EMBEDDINGS_ID_AITEST_AITEST string = embeddings_deployment_aitest_aitest.id
output AZURE_AI_EMBEDDINGS_NAME_AITEST_AITEST string = embeddings_deployment_aitest_aitest.name
output AZURE_AI_EMBEDDINGS_RESOURCE_GROUP_AITEST_AITEST string = resourceGroup().name
output AZURE_AI_EMBEDDINGS_MODEL_NAME_AITEST_AITEST string = embeddings_deployment_aitest_aitest.properties.model.name
output AZURE_AI_EMBEDDINGS_MODEL_VERSION_AITEST_AITEST string = embeddings_deployment_aitest_aitest.properties.model.version
output AZURE_AI_EMBEDDINGS_ENDPOINT_AITEST_AITEST string = '${aiservices_account_aitest.properties.endpoint}openai/deployments/${embeddings_deployment_aitest_aitest.name}'


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



resource keyvalue_azureaiaiservicesidaitest 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_AI_AISERVICES_ID_AITEST'
  properties: {
    value: aiservices_account_aitest.id
  }
}



resource keyvalue_azureaiaiservicesnameaitest 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_AI_AISERVICES_NAME_AITEST'
  properties: {
    value: aiservices_account_aitest.name
  }
}



resource keyvalue_azureaiaiservicesresourcegroupaitest 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_AI_AISERVICES_RESOURCE_GROUP_AITEST'
  properties: {
    value: resourceGroup().name
  }
}



resource keyvalue_azureaiaiservicesendpointaitest 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_AI_AISERVICES_ENDPOINT_AITEST'
  properties: {
    value: aiservices_account_aitest.properties.endpoint
  }
}



resource keyvalue_azureaiembeddingsidaitestaitest 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_AI_EMBEDDINGS_ID_AITEST_AITEST'
  properties: {
    value: embeddings_deployment_aitest_aitest.id
  }
}



resource keyvalue_azureaiembeddingsnameaitestaitest 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_AI_EMBEDDINGS_NAME_AITEST_AITEST'
  properties: {
    value: embeddings_deployment_aitest_aitest.name
  }
}



resource keyvalue_azureaiembeddingsresourcegroupaitestaitest 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_AI_EMBEDDINGS_RESOURCE_GROUP_AITEST_AITEST'
  properties: {
    value: resourceGroup().name
  }
}



resource keyvalue_azureaiembeddingsmodelnameaitestaitest 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_AI_EMBEDDINGS_MODEL_NAME_AITEST_AITEST'
  properties: {
    value: embeddings_deployment_aitest_aitest.properties.model.name
  }
}



resource keyvalue_azureaiembeddingsmodelversionaitestaitest 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_AI_EMBEDDINGS_MODEL_VERSION_AITEST_AITEST'
  properties: {
    value: embeddings_deployment_aitest_aitest.properties.model.version
  }
}



resource keyvalue_azureaiembeddingsendpointaitestaitest 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_AI_EMBEDDINGS_ENDPOINT_AITEST_AITEST'
  properties: {
    value: '${aiservices_account_aitest.properties.endpoint}openai/deployments/${embeddings_deployment_aitest_aitest.name}'
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



