# Release History

## 1.0.0 (2026-10-29)

### Features Added

  - Model `FileShare` added property `identity`
  - Model `FileShareProperties` added property `encryption`
  - Model `FileShareProperties` added property `migration_state`
  - Model `FileShareProperties` added property `scale_mode`
  - Model `FileShareProvisioningRecommendationInput` added property `media_tier`
  - Model `FileShareProvisioningRecommendationInput` added property `protocol`
  - Model `FileShareProvisioningRecommendationInput` added property `scale_mode`
  - Model `FileShareUpdate` added property `identity`
  - Model `FileShareUpdateProperties` added property `encryption`
  - Enum `MediaTier` added member `HDD`
  - Added model `CustomerManagedKeyEncryption`
  - Added model `FileShareEncryption`
  - Added model `FileShareLimitsRequest`
  - Added model `FileShareOfferInput`
  - Added enum `InfrastructureEncryption`
  - Added model `KeyEncryptionKeyIdentity`
  - Added enum `KeyEncryptionKeyIdentityType`
  - Added model `ManagedServiceIdentity`
  - Added enum `ManagedServiceIdentityType`
  - Added model `MigrationState`
  - Added enum `RedundancyConversionStatus`
  - Added model `RedundancyConversionStatusOutput`
  - Added model `RedundancyConversionStatusResponse`
  - Added enum `ScaleMode`
  - Added model `StartRedundancyConversionInput`
  - Added model `StartRedundancyConversionRequest`
  - Added model `UserAssignedIdentity`
  - Model `FileSharesOperations` added method `get_redundancy_conversion_status`
  - Model `FileSharesOperations` added method `start_redundancy_conversion`
  - Model `InformationalOperationsOperations` added parameter `content_type` in method `get_limits`

## 1.0.0b1 (2026-05-06)

### Other Changes

  - Initial version