# Release History

## 1.0.0b2 (2026-08-24)

### Features Added

  - Model `AttentionReason` added property `discovery_rule_exists`
  - Model `AttentionReason` added property `drill_rbac_on_health_model`
  - Model `AttentionReason` added property `drill_rbac_on_sli`
  - Model `AttentionReason` added property `health_model_exists`
  - Model `AttentionReason` added property `monitoring_source_not_configured`
  - Model `AttentionReason` added property `rbac_needed_for_drill_on_health_model`
  - Model `AttentionReason` added property `sli_attention_statuses`
  - Model `DrillProperties` added property `health_model_monitoring_properties`
  - Model `DrillProperties` added property `sli_monitoring_properties`
  - Model `DrillRunProperties` added property `report`
  - Model `DrillUpdateProperties` added property `health_model_monitoring_properties`
  - Model `DrillUpdateProperties` added property `sli_monitoring_properties`
  - Model `GoalAssignmentProperties` added property `require_zonal_resiliency`
  - Model `GoalResourceProperties` added property `zonal_resiliency`
  - Model `OperationQualificationDetails` added property `resource_feasibility_reviews`
  - Enum `ProvisioningState` added member `NEEDS_ATTENTION`
  - Model `RegionalDrillProperties` added property `health_model_monitoring_properties`
  - Model `RegionalDrillProperties` added property `sli_monitoring_properties`
  - Model `ValidateForExecutionProperties` added property `operation_name`
  - Model `ZonalDrillProperties` added property `health_model_monitoring_properties`
  - Model `ZonalDrillProperties` added property `sli_monitoring_properties`
  - Added enum `DrillReportFinalizationState`
  - Added enum `DrillReportFormat`
  - Added enum `DrillReportGenerationStatus`
  - Added model `DrillReportSummary`
  - Added model `DrillRunReprotectRequest`
  - Added enum `DrillRunTasks`
  - Added model `HealthModelMonitoringProperties`
  - Added model `ListReportDownloadUrlRequest`
  - Added model `ListReportDownloadUrlResponse`
  - Added model `ReportStageStatus`
  - Added model `ResiliencyProperties`
  - Added model `ResourceCrossZoneVmRecoveryProtectionSetting`
  - Added model `ResourceFeasibilityReview`
  - Added enum `ResourceFeasibilityReviewStatus`
  - Added enum `ResourceFeasibilityReviewType`
  - Added model `SkuDetails`
  - Added model `SliAttentionStatus`
  - Added model `SliMonitoringProperties`
  - Added model `SliSelection`
  - Added enum `SliType`
  - Added enum `SliTypeMatchState`
  - Added model `UserConfirmationItem`
  - Model `DrillRunsOperations` added parameter `content_type` in method `begin_reprotect`
  - Model `DrillRunsOperations` added method `begin_generate_report`
  - Model `DrillRunsOperations` added method `list_report_download_url`

### Breaking Changes

  - Model `DrillProperties` deleted or renamed its instance variable `managed_on_behalf_of_configuration`
  - Model `RegionalDrillProperties` deleted or renamed its instance variable `managed_on_behalf_of_configuration`
  - Model `ZonalDrillProperties` deleted or renamed its instance variable `managed_on_behalf_of_configuration`
  - Deleted or renamed model `ManagedOnBehalfOfConfiguration`
  - Deleted or renamed model `MoboBrokerResource`
  - Deleted or renamed model `UserConfirmationForHighAvailabilityItem`

## 1.0.0b1 (2026-06-16)

### Other Changes

  - Initial version
