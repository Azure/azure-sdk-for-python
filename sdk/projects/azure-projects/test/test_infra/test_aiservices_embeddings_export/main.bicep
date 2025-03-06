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

@sys.description('The Azure Active Directory tenant ID.')
param tenantId string = subscription().tenantId

@sys.description('Tags to apply to all resources in AZD environment.')
var azdTags = {
  'azd-env-name': environmentName
}

param aiEmbeddingsModel string = 'text-embedding-ada-002'

param aiEmbeddingsModelFormat string = 'OpenAI'

param aiEmbeddingsModelVersion string = '2'

param aiEmbeddingsModelSku string = 'Standard'

param aiEmbeddingsModelCapacity int = 30

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
    aiEmbeddingsModel: aiEmbeddingsModel
    aiEmbeddingsModelFormat: aiEmbeddingsModelFormat
    aiEmbeddingsModelVersion: aiEmbeddingsModelVersion
    aiEmbeddingsModelSku: aiEmbeddingsModelSku
    aiEmbeddingsModelCapacity: aiEmbeddingsModelCapacity
  }
}
output AZURE_AI_AISERVICES_ID string = test_module.outputs.AZURE_AI_AISERVICES_ID
output AZURE_AI_AISERVICES_NAME string = test_module.outputs.AZURE_AI_AISERVICES_NAME
output AZURE_AI_AISERVICES_RESOURCE_GROUP string = test_module.outputs.AZURE_AI_AISERVICES_RESOURCE_GROUP
output AZURE_AI_AISERVICES_ENDPOINT string = test_module.outputs.AZURE_AI_AISERVICES_ENDPOINT
output AZURE_AI_EMBEDDINGS_ID string = test_module.outputs.AZURE_AI_EMBEDDINGS_ID
output AZURE_AI_EMBEDDINGS_NAME string = test_module.outputs.AZURE_AI_EMBEDDINGS_NAME
output AZURE_AI_EMBEDDINGS_RESOURCE_GROUP string = test_module.outputs.AZURE_AI_EMBEDDINGS_RESOURCE_GROUP
output AZURE_AI_EMBEDDINGS_MODEL_NAME string = test_module.outputs.AZURE_AI_EMBEDDINGS_MODEL_NAME
output AZURE_AI_EMBEDDINGS_MODEL_VERSION string = test_module.outputs.AZURE_AI_EMBEDDINGS_MODEL_VERSION
output AZURE_AI_EMBEDDINGS_ENDPOINT string = test_module.outputs.AZURE_AI_EMBEDDINGS_ENDPOINT


