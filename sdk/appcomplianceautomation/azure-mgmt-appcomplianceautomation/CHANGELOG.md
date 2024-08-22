# Release History

## 1.0.0 (2024-06-23)

### Features Added

  - Added operation ReportOperations.begin_fix
  - Added operation ReportOperations.begin_sync_cert_record
  - Added operation ReportOperations.begin_verify
  - Added operation ReportOperations.get_scoping_questions
  - Added operation ReportOperations.list
  - Added operation ReportOperations.nested_resource_check_name_availability
  - Added operation SnapshotOperations.list
  - Added operation group EvidenceOperations
  - Added operation group ProviderActionsOperations
  - Added operation group ScopingConfigurationOperations
  - Added operation group WebhookOperations
  - Model ComplianceReportItem has a new parameter control_family_name
  - Model ComplianceReportItem has a new parameter control_status
  - Model ComplianceReportItem has a new parameter resource_origin
  - Model ComplianceReportItem has a new parameter resource_status
  - Model ComplianceReportItem has a new parameter resource_status_change_date
  - Model ComplianceReportItem has a new parameter responsibility_description
  - Model ComplianceReportItem has a new parameter responsibility_title
  - Model Control has a new parameter control_name
  - Model Control has a new parameter responsibilities
  - Model ControlFamily has a new parameter control_family_name
  - Model ControlFamily has a new parameter control_family_status
  - Model OverviewStatus has a new parameter not_applicable_count
  - Model OverviewStatus has a new parameter pending_count
  - Model ReportProperties has a new parameter cert_records
  - Model ReportProperties has a new parameter errors
  - Model ReportProperties has a new parameter storage_info
  - Model ResourceMetadata has a new parameter account_id
  - Model ResourceMetadata has a new parameter resource_origin

### Breaking Changes

  - Client name is changed from `AppComplianceAutomationToolForMicrosoft365` to `AppComplianceAutomationMgmtClient`
  - Model Category no longer has parameter category_type
  - Model ComplianceReportItem no longer has parameter compliance_state
  - Model ComplianceReportItem no longer has parameter control_type
  - Model ComplianceReportItem no longer has parameter policy_description
  - Model ComplianceReportItem no longer has parameter policy_display_name
  - Model ComplianceReportItem no longer has parameter policy_id
  - Model ComplianceReportItem no longer has parameter resource_group
  - Model ComplianceReportItem no longer has parameter status_change_date
  - Model ComplianceReportItem no longer has parameter subscription_id
  - Model Control no longer has parameter assessments
  - Model Control no longer has parameter control_short_name
  - Model Control no longer has parameter control_type
  - Model ControlFamily no longer has parameter family_name
  - Model ControlFamily no longer has parameter family_status
  - Model ControlFamily no longer has parameter family_type
  - Model ReportProperties no longer has parameter id
  - Model ReportProperties no longer has parameter report_name
  - Model ResourceMetadata no longer has parameter resource_name
  - Model ResourceMetadata no longer has parameter tags
  - Model SnapshotProperties no longer has parameter id
  - Operation ReportOperations.begin_create_or_update has a new required parameter properties
  - Operation ReportOperations.begin_create_or_update no longer has parameter parameters
  - Operation ReportOperations.begin_update has a new required parameter properties
  - Operation ReportOperations.begin_update no longer has parameter parameters
  - Operation SnapshotOperations.begin_download has a new required parameter body
  - Operation SnapshotOperations.begin_download no longer has parameter parameters
  - Removed operation group ReportsOperations
  - Removed operation group SnapshotsOperations

## 1.0.0b1 (2022-11-15)

* Initial Release
