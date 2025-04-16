param location string
param environmentName string
param defaultNamePrefix string
param defaultName string
param principalId string
param tenantId string
param azdTags object

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
}

output AZURE_APPCONFIG_ID string = configurationstore.id
output AZURE_APPCONFIG_NAME string = configurationstore.name
output AZURE_APPCONFIG_RESOURCE_GROUP string = resourceGroup().name
output AZURE_APPCONFIG_ENDPOINT string = configurationstore.properties.endpoint


resource aiservices_account_aitest 'Microsoft.CognitiveServices/accounts@2024-10-01' existing = {
  name: 'aitest'
}

output AZURE_AI_AISERVICES_ID_R string = aiservices_account_aitest.id
output AZURE_AI_AISERVICES_NAME_R string = aiservices_account_aitest.name
output AZURE_AI_AISERVICES_RESOURCE_GROUP_R string = resourceGroup().name
output AZURE_AI_AISERVICES_ENDPOINT_R string = aiservices_account_aitest.properties.endpoint


resource embeddings_deployment_aitest_aitest 'Microsoft.CognitiveServices/accounts/deployments@2024-10-01' existing = {
  name: 'aitest'
  parent: aiservices_account_aitest
}

output AZURE_AI_EMBEDDINGS_ID_R string = embeddings_deployment_aitest_aitest.id
output AZURE_AI_EMBEDDINGS_NAME_R string = embeddings_deployment_aitest_aitest.name
output AZURE_AI_EMBEDDINGS_RESOURCE_GROUP_R string = resourceGroup().name
output AZURE_AI_EMBEDDINGS_MODEL_NAME_R string = embeddings_deployment_aitest_aitest.properties.model.name
output AZURE_AI_EMBEDDINGS_MODEL_VERSION_R string = embeddings_deployment_aitest_aitest.properties.model.version
output AZURE_AI_EMBEDDINGS_MODEL_FORMAT_R string = embeddings_deployment_aitest_aitest.properties.model.format
output AZURE_AI_EMBEDDINGS_ENDPOINT_R string = '${aiservices_account_aitest.properties.endpoint}openai/deployments/${embeddings_deployment_aitest_aitest.name}'


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



resource keyvalue_azureaiaiservicesidr 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_AI_AISERVICES_ID_R'
  properties: {
    value: aiservices_account_aitest.id
  }
}



resource keyvalue_azureaiaiservicesnamer 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_AI_AISERVICES_NAME_R'
  properties: {
    value: aiservices_account_aitest.name
  }
}



resource keyvalue_azureaiaiservicesresourcegroupr 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_AI_AISERVICES_RESOURCE_GROUP_R'
  properties: {
    value: resourceGroup().name
  }
}



resource keyvalue_azureaiaiservicesendpointr 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_AI_AISERVICES_ENDPOINT_R'
  properties: {
    value: aiservices_account_aitest.properties.endpoint
  }
}



resource keyvalue_azureaiembeddingsidr 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_AI_EMBEDDINGS_ID_R'
  properties: {
    value: embeddings_deployment_aitest_aitest.id
  }
}



resource keyvalue_azureaiembeddingsnamer 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_AI_EMBEDDINGS_NAME_R'
  properties: {
    value: embeddings_deployment_aitest_aitest.name
  }
}



resource keyvalue_azureaiembeddingsresourcegroupr 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_AI_EMBEDDINGS_RESOURCE_GROUP_R'
  properties: {
    value: resourceGroup().name
  }
}



resource keyvalue_azureaiembeddingsmodelnamer 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_AI_EMBEDDINGS_MODEL_NAME_R'
  properties: {
    value: embeddings_deployment_aitest_aitest.properties.model.name
  }
}



resource keyvalue_azureaiembeddingsmodelversionr 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_AI_EMBEDDINGS_MODEL_VERSION_R'
  properties: {
    value: embeddings_deployment_aitest_aitest.properties.model.version
  }
}



resource keyvalue_azureaiembeddingsmodelformatr 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_AI_EMBEDDINGS_MODEL_FORMAT_R'
  properties: {
    value: embeddings_deployment_aitest_aitest.properties.model.format
  }
}



resource keyvalue_azureaiembeddingsendpointr 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_AI_EMBEDDINGS_ENDPOINT_R'
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



