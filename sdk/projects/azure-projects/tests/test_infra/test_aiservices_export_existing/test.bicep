param location string
param environmentName string
param defaultNamePrefix string
param defaultName string
param principalId string
param tenantId string
param azdTags object

resource aiservices_account_aitest 'Microsoft.CognitiveServices/accounts@2024-10-01' existing = {
  name: 'aitest'
}

output AZURE_AI_AISERVICES_ID_AITEST string = aiservices_account_aitest.id
output AZURE_AI_AISERVICES_NAME_AITEST string = aiservices_account_aitest.name
output AZURE_AI_AISERVICES_RESOURCE_GROUP_AITEST string = resourceGroup().name
output AZURE_AI_AISERVICES_ENDPOINT_AITEST string = aiservices_account_aitest.properties.endpoint


