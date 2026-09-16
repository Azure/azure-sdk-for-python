# Release History

## 1.0.0b2 (2026-09-16)

### Features Added

  - Client `ContainerServiceAIManagerMgmtClient` added operation group `custom_ai_models`
  - Model `AIManagerProperties` added property `cluster_resource_id`
  - Model `CredentialValue` added property `managed_identity`
  - Model `ModelSourceProperties` added property `microsoft_foundry`
  - Enum `ModelSourceType` added member `MICROSOFT_FOUNDRY`
  - Added model `BaseModelReference`
  - Added model `CustomAIModel`
  - Added model `CustomAIModelProperties`
  - Added enum `CustomAIModelProvisioningState`
  - Added model `CustomAIModelSpec`
  - Added model `ManagedIdentityCredential`
  - Added model `MicrosoftFoundrySource`
  - Added operation group `CustomAIModelsOperations`

### Breaking Changes

  - Deleted or renamed model `CalculateCostRequest`
  - Method `AIModelsOperations.calculate_cost` deleted or renamed its parameter `body` of kind `positional_or_keyword`
  - `AIModelsOperations.calculate_cost` had all overloads removed

## 1.0.0b1 (2026-08-05)

### Other Changes

  - Initial version