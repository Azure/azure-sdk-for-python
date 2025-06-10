# Release History

## 2.0.0b1 (2025-05-08)

### Features Added

  - Client `IoTFirmwareDefenseMgmtClient` added operation group `usage_metrics`
  - Model `BinaryHardeningFeatures` added property `no_execute`
  - Model `BinaryHardeningFeatures` added property `position_independent_executable`
  - Model `BinaryHardeningFeatures` added property `relocation_read_only`
  - Model `BinaryHardeningResult` added property `security_hardening_features`
  - Model `BinaryHardeningResult` added property `executable_architecture`
  - Model `BinaryHardeningResult` added property `executable_class`
  - Model `BinaryHardeningResult` added property `provisioning_state`
  - Model `BinaryHardeningSummaryResource` added property `not_executable_stack_count`
  - Model `BinaryHardeningSummaryResource` added property `position_independent_executable_count`
  - Model `BinaryHardeningSummaryResource` added property `relocation_read_only_count`
  - Model `BinaryHardeningSummaryResource` added property `stack_canary_count`
  - Model `BinaryHardeningSummaryResource` added property `stripped_binary_count`
  - Model `BinaryHardeningSummaryResource` added property `provisioning_state`
  - Model `CryptoCertificate` added property `certificate_name`
  - Model `CryptoCertificate` added property `certificate_role`
  - Model `CryptoCertificate` added property `certificate_key_size`
  - Model `CryptoCertificate` added property `certificate_key_algorithm`
  - Model `CryptoCertificate` added property `certificate_usage`
  - Model `CryptoCertificate` added property `provisioning_state`
  - Model `CryptoCertificateSummaryResource` added property `total_certificate_count`
  - Model `CryptoCertificateSummaryResource` added property `paired_key_count`
  - Model `CryptoCertificateSummaryResource` added property `expired_certificate_count`
  - Model `CryptoCertificateSummaryResource` added property `expiring_soon_certificate_count`
  - Model `CryptoCertificateSummaryResource` added property `weak_signature_count`
  - Model `CryptoCertificateSummaryResource` added property `self_signed_certificate_count`
  - Model `CryptoCertificateSummaryResource` added property `short_key_size_count`
  - Model `CryptoCertificateSummaryResource` added property `provisioning_state`
  - Model `CryptoKey` added property `crypto_key_size`
  - Model `CryptoKey` added property `provisioning_state`
  - Model `CryptoKeySummaryResource` added property `total_key_count`
  - Model `CryptoKeySummaryResource` added property `public_key_count`
  - Model `CryptoKeySummaryResource` added property `private_key_count`
  - Model `CryptoKeySummaryResource` added property `paired_key_count`
  - Model `CryptoKeySummaryResource` added property `short_key_size_count`
  - Model `CryptoKeySummaryResource` added property `provisioning_state`
  - Model `CveResult` added property `component_id`
  - Model `CveResult` added property `component_name`
  - Model `CveResult` added property `component_version`
  - Model `CveResult` added property `cve_name`
  - Model `CveResult` added property `effective_cvss_score`
  - Model `CveResult` added property `effective_cvss_version`
  - Model `CveResult` added property `cvss_scores`
  - Model `CveResult` added property `provisioning_state`
  - Model `CveSummary` added property `critical_cve_count`
  - Model `CveSummary` added property `high_cve_count`
  - Model `CveSummary` added property `medium_cve_count`
  - Model `CveSummary` added property `low_cve_count`
  - Model `CveSummary` added property `unknown_cve_count`
  - Model `CveSummary` added property `provisioning_state`
  - Model `FirmwareSummary` added property `provisioning_state`
  - Model `PairedKey` added property `paired_key_id`
  - Model `PasswordHash` added property `provisioning_state`
  - Enum `ProvisioningState` added member `ANALYZING`
  - Enum `ProvisioningState` added member `EXTRACTING`
  - Enum `ProvisioningState` added member `PENDING`
  - Model `SbomComponent` added property `provisioning_state`
  - Model `SummaryResourceProperties` added property `provisioning_state`
  - Enum `SummaryType` added member `COMMON_VULNERABILITIES_AND_EXPOSURES`
  - Model `Workspace` added property `sku`
  - Added enum `CertificateUsage`
  - Added enum `CryptoKeyType`
  - Added model `CvssScore`
  - Added enum `ExecutableClass`
  - Added model `ProxyResource`
  - Added model `Sku`
  - Added enum `SkuTier`
  - Added model `UsageMetric`
  - Added model `UsageMetricProperties`
  - Added model `WorkspaceUpdate`
  - Added operation group `UsageMetricsOperations`

### Breaking Changes

  - Model `BinaryHardeningFeatures` deleted or renamed its instance variable `nx`
  - Model `BinaryHardeningFeatures` deleted or renamed its instance variable `pie`
  - Model `BinaryHardeningFeatures` deleted or renamed its instance variable `relro`
  - Model `BinaryHardeningResult` deleted or renamed its instance variable `features`
  - Model `BinaryHardeningResult` deleted or renamed its instance variable `architecture`
  - Model `BinaryHardeningResult` deleted or renamed its instance variable `class_property`
  - Model `BinaryHardeningSummaryResource` deleted or renamed its instance variable `nx`
  - Model `BinaryHardeningSummaryResource` deleted or renamed its instance variable `pie`
  - Model `BinaryHardeningSummaryResource` deleted or renamed its instance variable `relro`
  - Model `BinaryHardeningSummaryResource` deleted or renamed its instance variable `canary`
  - Model `BinaryHardeningSummaryResource` deleted or renamed its instance variable `stripped`
  - Model `CryptoCertificate` deleted or renamed its instance variable `name`
  - Model `CryptoCertificate` deleted or renamed its instance variable `role`
  - Model `CryptoCertificate` deleted or renamed its instance variable `key_size`
  - Model `CryptoCertificate` deleted or renamed its instance variable `key_algorithm`
  - Model `CryptoCertificate` deleted or renamed its instance variable `usage`
  - Model `CryptoCertificateSummaryResource` deleted or renamed its instance variable `total_certificates`
  - Model `CryptoCertificateSummaryResource` deleted or renamed its instance variable `paired_keys`
  - Model `CryptoCertificateSummaryResource` deleted or renamed its instance variable `expired`
  - Model `CryptoCertificateSummaryResource` deleted or renamed its instance variable `expiring_soon`
  - Model `CryptoCertificateSummaryResource` deleted or renamed its instance variable `weak_signature`
  - Model `CryptoCertificateSummaryResource` deleted or renamed its instance variable `self_signed`
  - Model `CryptoCertificateSummaryResource` deleted or renamed its instance variable `short_key_size`
  - Model `CryptoKey` deleted or renamed its instance variable `key_size`
  - Model `CryptoKeySummaryResource` deleted or renamed its instance variable `total_keys`
  - Model `CryptoKeySummaryResource` deleted or renamed its instance variable `public_keys`
  - Model `CryptoKeySummaryResource` deleted or renamed its instance variable `private_keys`
  - Model `CryptoKeySummaryResource` deleted or renamed its instance variable `paired_keys`
  - Model `CryptoKeySummaryResource` deleted or renamed its instance variable `short_key_size`
  - Model `CveResult` deleted or renamed its instance variable `component`
  - Model `CveResult` deleted or renamed its instance variable `name`
  - Model `CveResult` deleted or renamed its instance variable `cvss_score`
  - Model `CveResult` deleted or renamed its instance variable `cvss_version`
  - Model `CveResult` deleted or renamed its instance variable `cvss_v2_score`
  - Model `CveResult` deleted or renamed its instance variable `cvss_v3_score`
  - Model `CveSummary` deleted or renamed its instance variable `critical`
  - Model `CveSummary` deleted or renamed its instance variable `high`
  - Model `CveSummary` deleted or renamed its instance variable `medium`
  - Model `CveSummary` deleted or renamed its instance variable `low`
  - Model `CveSummary` deleted or renamed its instance variable `unknown`
  - Model `PairedKey` deleted or renamed its instance variable `id`
  - Deleted or renamed enum value `ProvisioningState.ACCEPTED`
  - Deleted or renamed enum value `SummaryType.CVE`
  - Deleted or renamed model `CveComponent`
  - Deleted or renamed model `FirmwareList`
  - Deleted or renamed model `SummaryName`
  - Deleted or renamed model `WorkspaceList`
  - Deleted or renamed model `WorkspaceUpdateDefinition`
  - Method `FirmwaresOperations.create` renamed its instance variable `firmware` to `resource`
  - Method `FirmwaresOperations.update` renamed its instance variable `firmware` to `properties`
  - Deleted or renamed method `FirmwaresOperations.generate_download_url`
  - Deleted or renamed method `FirmwaresOperations.generate_filesystem_download_url`
  - Method `SummariesOperations.get` renamed its instance variable `summary_name` to `summary_type`
  - Method `WorkspacesOperations.create` renamed its instance variable `workspace` to `resource`
  - Method `WorkspacesOperations.generate_upload_url` renamed its instance variable `generate_upload_url` to `body`
  - Method `WorkspacesOperations.update` renamed its instance variable `workspace` to `properties`

## 1.0.0 (2024-03-27)

### Features Added

  - Added operation group BinaryHardeningOperations
  - Added operation group CryptoCertificatesOperations
  - Added operation group CryptoKeysOperations
  - Added operation group CvesOperations
  - Added operation group FirmwaresOperations
  - Added operation group PasswordHashesOperations
  - Added operation group SbomComponentsOperations
  - Added operation group SummariesOperations
  - Model Firmware has a new parameter properties
  - Model FirmwareUpdateDefinition has a new parameter properties
  - Model Workspace has a new parameter properties
  - Model WorkspaceUpdateDefinition has a new parameter properties

### Breaking Changes

  - Model CveSummary has a new required parameter summary_type
  - Model CveSummary no longer has parameter undefined
  - Model Firmware no longer has parameter description
  - Model Firmware no longer has parameter file_name
  - Model Firmware no longer has parameter file_size
  - Model Firmware no longer has parameter model
  - Model Firmware no longer has parameter provisioning_state
  - Model Firmware no longer has parameter status
  - Model Firmware no longer has parameter status_messages
  - Model Firmware no longer has parameter vendor
  - Model Firmware no longer has parameter version
  - Model FirmwareSummary has a new required parameter summary_type
  - Model FirmwareUpdateDefinition no longer has parameter description
  - Model FirmwareUpdateDefinition no longer has parameter file_name
  - Model FirmwareUpdateDefinition no longer has parameter file_size
  - Model FirmwareUpdateDefinition no longer has parameter model
  - Model FirmwareUpdateDefinition no longer has parameter provisioning_state
  - Model FirmwareUpdateDefinition no longer has parameter status
  - Model FirmwareUpdateDefinition no longer has parameter status_messages
  - Model FirmwareUpdateDefinition no longer has parameter vendor
  - Model FirmwareUpdateDefinition no longer has parameter version
  - Model PairedKey no longer has parameter additional_properties
  - Model UrlToken no longer has parameter upload_url
  - Model Workspace no longer has parameter provisioning_state
  - Model WorkspaceUpdateDefinition no longer has parameter provisioning_state
  - Removed operation group FirmwareOperations

## 1.0.0b1 (2023-07-24)

* Initial Release
