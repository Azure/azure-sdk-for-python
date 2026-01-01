# Release History

## 1.0.0 (2025-12-30)

### Features Added

  - Model `HealthBotProperties` added property `access_control_method`
  - Enum `SkuName` added member `C1`
  - Enum `SkuName` added member `PES`
  - Added enum `CreatedByType`
  - Model `BotsOperations` added method `begin_update`

### Breaking Changes

  - Deleted or renamed client `HealthBotMgmtClient`
  - Deleted or renamed enum value `SkuName.S1`
  - Deleted or renamed model `AvailableOperations`
  - Deleted or renamed model `BotResponseList`
  - Deleted or renamed model `IdentityType`
  - Deleted or renamed model `ValidationResult`
  - Deleted or renamed method `BotsOperations.update`

## 1.0.0b2 (2022-10-28)

### Features Added

  - Added operation BotsOperations.list_secrets
  - Added operation BotsOperations.regenerate_api_jwt_secret
  - Model HealthBot has a new parameter identity
  - Model HealthBotProperties has a new parameter key_vault_properties
  - Model HealthBotUpdateParameters has a new parameter identity
  - Model HealthBotUpdateParameters has a new parameter location
  - Model HealthBotUpdateParameters has a new parameter properties

### Breaking Changes

  - Client name is changed from `Healthbot` to `HealthBotMgmtClient`

## 1.0.0b1 (2021-01-06)

* Initial Release
