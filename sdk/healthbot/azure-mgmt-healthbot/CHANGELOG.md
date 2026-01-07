# Release History

## 1.0.0 (2026-01-06)

### Features Added

  - Model `HealthBotMgmtClient` added parameter `cloud_setting` in method `__init__`
  - Client `HealthBotMgmtClient` added method `send_request`
  - Model `HealthBotProperties` added property `access_control_method`
  - Enum `SkuName` added member `C1`
  - Enum `SkuName` added member `PES`

### Breaking Changes

  - Deleted or renamed enum value `SkuName.S1`
  - Renamed enum `IdentityType` to `CreatedByType`
  - Renamed method `BotsOperations.update` to `begin_update`

### Other Changes

  - Deleted model `AvailableOperations`/`BotResponseList`/`ValidationResult` which actually were not used by SDK users

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
