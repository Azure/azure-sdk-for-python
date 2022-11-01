# Azure Personalizer Client for Python

> see https://aka.ms/autorest

### Setup

Install Autorest v3

```ps
npm install -g autorest
```

### Generation

```ps
cd <swagger-folder>
autorest
```

### Settings

```yaml
namespace: azure.ai.personalizer
package-name: azure-ai-personalizer
license-header: MICROSOFT_MIT_NO_VERSION
clear-output-folder: true
no-namespace-folders: true
python: true
openapi-type: data-plane
version-tolerant: true
package-version: 1.0.0b1
add-credential: true
credential-default-policy-type: AzureKeyCredentialPolicy
credential-key-header-name: Ocp-Apim-Subscription-Key
black: true
```


## Runtime

```yaml
input-file: https://github.com/Azure/azure-rest-api-specs/blob/e24bbf6a66cb0a19c072c6f15cee163acbd7acf7/specification/cognitiveservices/data-plane/Personalizer/preview/2022-09-01-preview/Personalizer.json
output-folder: ../azure/ai/personalizer
title: PersonalizerClient
```

```yaml
directive:
  - where-operation: Evaluations_List
    transform: >
        $.parameters[1]["x-ms-client-name"] = "filter_expression";
  - rename-operation:
      from: Evaluations_List
      to: ListEvaluations
  - rename-operation:
      from: Evaluations_Get
      to: GetEvaluation
  - rename-operation:
      from: Evaluations_Delete
      to: DeleteEvaluation
  - rename-operation:
      from: Evaluations_Create
      to: CreateEvaluation
  - rename-operation:
      from: FeatureImportances_List
      to: ListFeatureImportances
  - rename-operation:
      from: FeatureImportances_Get
      to: GetFeatureImportance
  - rename-operation:
      from: FeatureImportances_Delete
      to: DeleteFeatureImportance
  - rename-operation:
      from: FeatureImportances_Create
      to: CreateFeatureImportance
  - rename-operation:
      from: ServiceConfiguration_Get
      to: GetServiceConfiguration
  - rename-operation:
      from: ServiceConfiguration_Update
      to: UpdateServiceConfiguration
  - rename-operation:
      from: ServiceConfiguration_ApplyFromEvaluation
      to: ApplyFromEvaluation
  - rename-operation:
      from: Policy_Get
      to: GetPolicy
  - rename-operation:
      from: Policy_Update
      to: UpdatePolicy
  - rename-operation:
      from: Policy_Update
      to: UpdatePolicy
  - rename-operation:
      from: Policy_Reset
      to: ResetPolicy
  - rename-operation:
      from: Log_Delete
      to: DeleteLog
  - rename-operation:
      from: Log_GetProperties
      to: GetLogProperties
  - rename-operation:
      from: Model_Get
      to: GetModel
  - rename-operation:
      from: Model_Import
      to: ImportModel
  - rename-operation:
      from: Model_Reset
      to: ResetModel
  - rename-operation:
      from: Model_GetProperties
      to: GetModelProperties
  - rename-operation:
      from: Rank
      to: RankSingleSlot
  - rename-operation:
      from: Events_Reward
      to: RewardSingleSlotEvent
  - rename-operation:
      from: Events_Activate
      to: ActivateSingleSlotEvent
  - rename-operation:
      from: MultiSlot_Rank
      to: RankMultiSlot
  - rename-operation:
      from: MultiSlotEvents_Reward
      to: RewardMultiSlotEvent
  - rename-operation:
      from: MultiSlotEvents_Activate
      to: ActivateMultiSlotEvent
```