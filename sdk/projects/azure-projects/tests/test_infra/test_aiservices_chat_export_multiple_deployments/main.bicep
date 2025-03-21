targetScope = 'subscription'

@sys.description('Primary location for all resources')
@sys.minLength(1)
param location string

@sys.description('AZD environment name')
@sys.maxLength(64)
@sys.minLength(1)
param environmentName string

param defaultNamePrefix string = 'azproj'

param defaultName string = '${defaultNamePrefix}${uniqueString(subscription().subscriptionId, environmentName, location)}'

@sys.description('ID of the user or app to assign application roles')
param principalId string

@sys.secure()
@sys.description('The Azure Active Directory tenant ID.')
param tenantId string = subscription().tenantId

@sys.description('Tags to apply to all resources in AZD environment.')
var azdTags = {
  'azd-env-name': environmentName
}

param aiChatModelSku string = 'Standard'

param aiChatModelCapacity int = 30

resource resourcegroup 'Microsoft.Resources/resourceGroups@2021-04-01' = {
  name: defaultName
  location: location
  tags: azdTags
}

module test_module 'test.bicep' = {
  name: '${deployment().name}_test'
  scope: resourcegroup
  params: {
    location: location
    environmentName: environmentName
    defaultNamePrefix: defaultNamePrefix
    defaultName: defaultName
    principalId: principalId
    tenantId: tenantId
    azdTags: azdTags
    aiChatModelSku: aiChatModelSku
    aiChatModelCapacity: aiChatModelCapacity
  }
}
output AZURE_APPCONFIG_ID string = test_module.outputs.AZURE_APPCONFIG_ID
output AZURE_APPCONFIG_NAME string = test_module.outputs.AZURE_APPCONFIG_NAME
output AZURE_APPCONFIG_RESOURCE_GROUP string = test_module.outputs.AZURE_APPCONFIG_RESOURCE_GROUP
output AZURE_APPCONFIG_ENDPOINT string = test_module.outputs.AZURE_APPCONFIG_ENDPOINT
output AZURE_AI_AISERVICES_ID string = test_module.outputs.AZURE_AI_AISERVICES_ID
output AZURE_AI_AISERVICES_NAME string = test_module.outputs.AZURE_AI_AISERVICES_NAME
output AZURE_AI_AISERVICES_RESOURCE_GROUP string = test_module.outputs.AZURE_AI_AISERVICES_RESOURCE_GROUP
output AZURE_AI_AISERVICES_ENDPOINT string = test_module.outputs.AZURE_AI_AISERVICES_ENDPOINT
output AZURE_AI_CHAT_ID_ONE string = test_module.outputs.AZURE_AI_CHAT_ID_ONE
output AZURE_AI_CHAT_NAME_ONE string = test_module.outputs.AZURE_AI_CHAT_NAME_ONE
output AZURE_AI_CHAT_RESOURCE_GROUP_ONE string = test_module.outputs.AZURE_AI_CHAT_RESOURCE_GROUP_ONE
output AZURE_AI_CHAT_MODEL_NAME_ONE string = test_module.outputs.AZURE_AI_CHAT_MODEL_NAME_ONE
output AZURE_AI_CHAT_MODEL_VERSION_ONE string = test_module.outputs.AZURE_AI_CHAT_MODEL_VERSION_ONE
output AZURE_AI_CHAT_ENDPOINT_ONE string = test_module.outputs.AZURE_AI_CHAT_ENDPOINT_ONE
output AZURE_AI_CHAT_ID_TWO string = test_module.outputs.AZURE_AI_CHAT_ID_TWO
output AZURE_AI_CHAT_NAME_TWO string = test_module.outputs.AZURE_AI_CHAT_NAME_TWO
output AZURE_AI_CHAT_RESOURCE_GROUP_TWO string = test_module.outputs.AZURE_AI_CHAT_RESOURCE_GROUP_TWO
output AZURE_AI_CHAT_MODEL_NAME_TWO string = test_module.outputs.AZURE_AI_CHAT_MODEL_NAME_TWO
output AZURE_AI_CHAT_MODEL_VERSION_TWO string = test_module.outputs.AZURE_AI_CHAT_MODEL_VERSION_TWO
output AZURE_AI_CHAT_ENDPOINT_TWO string = test_module.outputs.AZURE_AI_CHAT_ENDPOINT_TWO


