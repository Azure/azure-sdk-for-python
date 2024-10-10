# Release History

## 1.0.0 (2024-10-07)

### Features Added

  - Enum `Origin` added member `CUSTOMER_ON_DEMAND`
  - Model `ServerForUpdate` added property `administrator_login`
  - Model `BackupsOperations` added method `begin_create`
  - Model `BackupsOperations` added method `begin_delete`

### Breaking Changes

  - Deleted or renamed client operation group `PostgreSQLManagementClient.quota_usages`
  - Deleted or renamed model `NameProperty`
  - Deleted or renamed model `QuotaUsage`
  - Deleted or renamed model `QuotaUsagesOperations`

### Other Changes

  - Upgrade api-version to `2024-08-01`
  - Storage auto growth
  - IOPS scaling
  - Backup - Long Term Retention
  - Backup - On-demand
  - Geo-redundant backup encryption key - Revive Dropped
  - Server Logs
  - Migrations
  - Migration Pre-validation
  - Migration Roles
  - Private endpoint Migration
  - Private Endpoints
  - Read replicas - Switchover
  - Read replicas - Virtual Endpoints
  - Azure Defender / Threat Protection APIs
  - PG 16 support
  - PremiumV2_LRS storage type support
  - Location capabilities updates

## 1.0.0b1 (2024-08-27)

### Other Changes

  - Initial version
