param location string
param environmentName string
param defaultNamePrefix string
param defaultName string
param principalId string
param tenantId string
param azdTags object
param aiChatModel string
param aiChatModelFormat string
param aiChatModelVersion string
param aiChatModelSku string
param aiChatModelCapacity int

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


resource aiservices_account 'Microsoft.CognitiveServices/accounts@2024-10-01' = {
  kind: 'AIServices'
  name: '${defaultName}-aiservices'
  location: location
  tags: azdTags
  sku: {
    name: 'S0'
  }
  properties: {
    publicNetworkAccess: 'Enabled'
    disableLocalAuth: true
    customSubDomainName: '${defaultName}-aiservices'
    networkAcls: {
      defaultAction: 'Allow'
    }
  }
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${userassignedidentity.id}': {}
    }
  }
}

output AZURE_AI_AISERVICES_ID_R string = aiservices_account.id
output AZURE_AI_AISERVICES_NAME_R string = aiservices_account.name
output AZURE_AI_AISERVICES_RESOURCE_GROUP_R string = resourceGroup().name
output AZURE_AI_AISERVICES_ENDPOINT_R string = aiservices_account.properties.endpoint


resource chat_deployment 'Microsoft.CognitiveServices/accounts/deployments@2024-10-01' = {
  parent: aiservices_account
  name: aiChatModel
  properties: {
    model: {
      name: aiChatModel
      format: aiChatModelFormat
      version: aiChatModelVersion
    }
  }
  sku: {
    name: aiChatModelSku
    capacity: aiChatModelCapacity
  }
}

output AZURE_AI_CHAT_ID_R string = chat_deployment.id
output AZURE_AI_CHAT_NAME_R string = chat_deployment.name
output AZURE_AI_CHAT_RESOURCE_GROUP_R string = resourceGroup().name
output AZURE_AI_CHAT_MODEL_NAME_R string = chat_deployment.properties.model.name
output AZURE_AI_CHAT_MODEL_VERSION_R string = chat_deployment.properties.model.version
output AZURE_AI_CHAT_MODEL_FORMAT_R string = chat_deployment.properties.model.format


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
    value: aiservices_account.id
  }
}



resource keyvalue_azureaiaiservicesnamer 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_AI_AISERVICES_NAME_R'
  properties: {
    value: aiservices_account.name
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
    value: aiservices_account.properties.endpoint
  }
}



resource keyvalue_azureaichatidr 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_AI_CHAT_ID_R'
  properties: {
    value: chat_deployment.id
  }
}



resource keyvalue_azureaichatnamer 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_AI_CHAT_NAME_R'
  properties: {
    value: chat_deployment.name
  }
}



resource keyvalue_azureaichatresourcegroupr 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_AI_CHAT_RESOURCE_GROUP_R'
  properties: {
    value: resourceGroup().name
  }
}



resource keyvalue_azureaichatmodelnamer 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_AI_CHAT_MODEL_NAME_R'
  properties: {
    value: chat_deployment.properties.model.name
  }
}



resource keyvalue_azureaichatmodelversionr 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_AI_CHAT_MODEL_VERSION_R'
  properties: {
    value: chat_deployment.properties.model.version
  }
}



resource keyvalue_azureaichatmodelformatr 'Microsoft.AppConfiguration/configurationStores/keyValues@2024-05-01' = {
  parent: configurationstore
  name: 'AZURE_AI_CHAT_MODEL_FORMAT_R'
  properties: {
    value: chat_deployment.properties.model.format
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



resource roleassignment_iwqyskxadwyqpexjwfcy 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftCognitiveServicesaccounts', environmentName, '${defaultName}-aiservices', 'ServicePrincipal', 'Cognitive Services OpenAI Contributor')
  properties: {
    principalId: userassignedidentity.properties.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      'a001fd3d-188f-4b5d-821b-7da978bf7442'
    )

  }
  scope: aiservices_account
}



resource roleassignment_hmfasjqbixwvwxlvyigx 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftCognitiveServicesaccounts', environmentName, '${defaultName}-aiservices', 'ServicePrincipal', 'Cognitive Services Contributor')
  properties: {
    principalId: userassignedidentity.properties.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      '25fbc0a9-bd7c-42a3-aa1a-3b75d497ee68'
    )

  }
  scope: aiservices_account
}



resource roleassignment_qiwviqlvorhviuoikyhn 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftCognitiveServicesaccounts', environmentName, '${defaultName}-aiservices', 'ServicePrincipal', 'Cognitive Services OpenAI User')
  properties: {
    principalId: userassignedidentity.properties.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      '5e0bd9bd-7b93-4f28-af87-19fc36ad61bd'
    )

  }
  scope: aiservices_account
}



resource roleassignment_vqsitscwkobrdvlojpeo 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftCognitiveServicesaccounts', environmentName, '${defaultName}-aiservices', 'ServicePrincipal', 'Cognitive Services User')
  properties: {
    principalId: userassignedidentity.properties.principalId
    principalType: 'ServicePrincipal'
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      'a97b65f3-24c7-4388-baec-2e87135dc908'
    )

  }
  scope: aiservices_account
}



resource roleassignment_djccqiqwpzkgpvmsxtpg 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftCognitiveServicesaccounts', environmentName, '${defaultName}-aiservices', 'User', 'Cognitive Services OpenAI Contributor')
  properties: {
    principalId: principalId
    principalType: 'User'
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      'a001fd3d-188f-4b5d-821b-7da978bf7442'
    )

  }
  scope: aiservices_account
}



resource roleassignment_rgqwxelwqrhtwxkejhyc 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftCognitiveServicesaccounts', environmentName, '${defaultName}-aiservices', 'User', 'Cognitive Services Contributor')
  properties: {
    principalId: principalId
    principalType: 'User'
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      '25fbc0a9-bd7c-42a3-aa1a-3b75d497ee68'
    )

  }
  scope: aiservices_account
}



resource roleassignment_eiambevcfusbcnjuoefk 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftCognitiveServicesaccounts', environmentName, '${defaultName}-aiservices', 'User', 'Cognitive Services OpenAI User')
  properties: {
    principalId: principalId
    principalType: 'User'
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      '5e0bd9bd-7b93-4f28-af87-19fc36ad61bd'
    )

  }
  scope: aiservices_account
}



resource roleassignment_ulmeiktaicqeonwxbgkw 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftCognitiveServicesaccounts', environmentName, '${defaultName}-aiservices', 'User', 'Cognitive Services User')
  properties: {
    principalId: principalId
    principalType: 'User'
    roleDefinitionId: subscriptionResourceId(
      'Microsoft.Authorization/roleDefinitions',
      'a97b65f3-24c7-4388-baec-2e87135dc908'
    )

  }
  scope: aiservices_account
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



