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


