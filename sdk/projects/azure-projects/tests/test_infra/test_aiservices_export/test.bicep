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



resource aiservices_account 'Microsoft.CognitiveServices/accounts@2024-10-01' = {
  kind: 'AIServices'
  properties: {
    publicNetworkAccess: 'Enabled'
    disableLocalAuth: true
    customSubDomainName: '${defaultName}-aiservices'
    networkAcls: {
      defaultAction: 'Allow'
      virtualNetworkRules: []
      ipRules: []
    }
  }
  name: '${defaultName}-aiservices'
  location: location
  tags: azdTags
  sku: {
    name: 'S0'
  }
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${userassignedidentity.id}': {}
    }
  }
}

output AZURE_AI_AISERVICES_ID string = aiservices_account.id
output AZURE_AI_AISERVICES_NAME string = aiservices_account.name
output AZURE_AI_AISERVICES_RESOURCE_GROUP string = resourceGroup().name
output AZURE_AI_AISERVICES_ENDPOINT string = aiservices_account.properties.endpoint


resource roleassignment_pqjisaqxrgcysgrhdblx 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftCognitiveServicesaccounts', '${defaultName}-aiservices', 'ServicePrincipal', 'Cognitive Services OpenAI Contributor')
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



resource roleassignment_wpbwavohdylvllgtoewg 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftCognitiveServicesaccounts', '${defaultName}-aiservices', 'ServicePrincipal', 'Cognitive Services Contributor')
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



resource roleassignment_mgufizgvzsqmbzqocksu 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftCognitiveServicesaccounts', '${defaultName}-aiservices', 'ServicePrincipal', 'Cognitive Services OpenAI User')
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



resource roleassignment_xmpyattycxterihwzhjs 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftCognitiveServicesaccounts', '${defaultName}-aiservices', 'ServicePrincipal', 'Cognitive Services User')
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



resource roleassignment_pjkjzujnwnqnlupkacxk 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftCognitiveServicesaccounts', '${defaultName}-aiservices', 'User', 'Cognitive Services OpenAI Contributor')
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



resource roleassignment_pqrtmtgtctxarhamusgu 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftCognitiveServicesaccounts', '${defaultName}-aiservices', 'User', 'Cognitive Services Contributor')
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



resource roleassignment_brzmmiebdqmayimhrmyf 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftCognitiveServicesaccounts', '${defaultName}-aiservices', 'User', 'Cognitive Services OpenAI User')
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



resource roleassignment_uowcqnnqpxydgmvubghf 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid('MicrosoftCognitiveServicesaccounts', '${defaultName}-aiservices', 'User', 'Cognitive Services User')
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



