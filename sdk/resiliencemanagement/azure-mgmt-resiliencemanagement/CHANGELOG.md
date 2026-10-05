# Release History

## 1.0.0b3 (2026-10-05)

### Features Added

  - Model `AttentionReason` added property `drill_rbac_on_goal_assignment`
  - Model `AttentionReason` added property `goal_assignment`
  - Model `AttentionReason` added property `health_model_associated_with_service_group`
  - Model `AttentionReason` added property `rbac_needed_for_drill_on_goal_assignment`
  - Model `AttentionReason` added property `recovery_plan`
  - Model `DrillProperties` added property `goal_assignment_properties`
  - Model `DrillResourceProperties` added property `drill_type`
  - Model `DrillResourceProperties` added property `fault_eligibility`
  - Model `DrillResourceProperties` added property `fault_ineligible_reason`
  - Model `DrillRunProperties` added property `recovery_time_objective`
  - Model `DrillUpdateProperties` added property `goal_assignment_properties`
  - Model `GoalAssignmentProperties` added property `regional_objectives`
  - Model `GoalAssignmentProperties` added property `require_regional_resiliency`
  - Model `GoalResourceProperties` added property `regional_resiliency`
  - Model `GoalsData` added property `regional_resiliency`
  - Model `GoalsData` added property `zonal_resiliency`
  - Model `HealthModelMonitoringProperties` added property `health_model_id`
  - Model `LastRunProperties` added property `last_run_recovery_time_actual`
  - Model `RecoveryResourceProperties` added property `inclusion_disabled_reasons`
  - Model `RegionalDrillProperties` added property `goal_assignment_properties`
  - Model `ResourceProtectionSolutionSettings` added property `replication_mode`
  - Enum `ResourceProtectionSolutionType` added member `AZURE_COSMOS_DB`
  - Enum `ResourceProtectionSolutionType` added member `AZURE_NET_APP_FILES`
  - Enum `ResourceProtectionSolutionType` added member `AZURE_SERVICE_BUS`
  - Enum `ResourceProtectionSolutionType` added member `AZURE_STORAGE_ACCOUNT`
  - Enum `ResourceProtectionSolutionType` added member `AZURE_TEMPLATE`
  - Model `UnifiedResilienceItemProperties` added property `billing_info`
  - Model `UnifiedResilienceItemProperties` added property `resiliency_posture`
  - Model `ZonalDrillProperties` added property `goal_assignment_properties`
  - Added enum `FaultEligibility`
  - Added enum `FaultIneligibleReason`
  - Added model `GoalAssignmentPropertiesOfDrill`
  - Added model `RegionalDrillResourceProperties`
  - Added model `RegionalObjectives`
  - Added enum `RegionalResiliencyStatus`
  - Added enum `ReplicationMode`
  - Added model `ResourceAzureTemplateProtectionSetting`
  - Added model `ResourceCosmosDBProtectionSetting`
  - Added enum `ResourceInclusionDisabledReason`
  - Added model `ResourceNetAppFilesProtectionSetting`
  - Added model `ResourceServiceBusProtectionSetting`
  - Added model `ResourceStorageAccountProtectionSetting`
  - Added model `UnifiedResilienceItemBillingInfo`
  - Added model `UnifiedResilienceItemGoalRequirement`
  - Added model `UnifiedResilienceItemRegionalResiliencyPosture`
  - Added model `UnifiedResilienceItemResiliencyPosture`
  - Added model `UnifiedResilienceItemZonalResiliencyPosture`
  - Added model `ZonalDrillResourceProperties`

### Breaking Changes

  - Deleted or renamed client operation group `ResilienceManagementClient.goal_templates`
  - Model `DrillResourceProperties` deleted or renamed its instance variable `active_physical_zones`
  - Model `DrillResourceProperties` deleted or renamed its instance variable `advisor_ha_recommendation_id`
  - Model `DrillResourceProperties` deleted or renamed its instance variable `ha_status`
  - Model `DrillResourceProperties` deleted or renamed its instance variable `recovery_physical_zones`
  - Model `GoalAssignmentProperties` deleted or renamed its instance variable `goal_assignment_type`
  - Model `GoalAssignmentProperties` deleted or renamed its instance variable `goal_template_id`
  - `GoalAssignmentProperties.require_zonal_resiliency` is now required.
  - Model `GoalResourceProperties` deleted or renamed its instance variable `disaster_recovery_attestation_status`
  - Model `GoalResourceProperties` deleted or renamed its instance variable `disaster_recovery_goal_participation`
  - Model `GoalResourceProperties` deleted or renamed its instance variable `exclusion_reason_for_disaster_recovery_goals`
  - Model `GoalResourceProperties` deleted or renamed its instance variable `exclusion_reason_for_high_availability_goals`
  - Model `GoalResourceProperties` deleted or renamed its instance variable `high_availability_attestation_status`
  - Model `GoalResourceProperties` deleted or renamed its instance variable `high_availability_goal_participation`
  - Model `GoalResourceProperties` deleted or renamed its instance variable `service_group_memberships`
  - Model `GoalResourceProperties` deleted or renamed its instance variable `user_confirmation_for_high_availability`
  - Model `GoalsData` deleted or renamed its instance variable `regional_recovery_point_estimated_in_minutes`
  - Model `GoalsData` deleted or renamed its instance variable `regional_recovery_point_objective_in_minutes`
  - Model `GoalsData` deleted or renamed its instance variable `regional_recovery_point_objective_status`
  - Model `GoalsData` deleted or renamed its instance variable `regional_recovery_time_actual_in_minutes`
  - Model `GoalsData` deleted or renamed its instance variable `regional_recovery_time_objective_in_minutes`
  - Model `GoalsData` deleted or renamed its instance variable `regional_recovery_time_objective_status`
  - Model `GoalsData` deleted or renamed its instance variable `require_disaster_recovery`
  - Model `GoalsData` deleted or renamed its instance variable `require_high_availability`
  - Model `GoalsData` deleted or renamed its instance variable `template_id`
  - Model `HealthModelMonitoringProperties` deleted or renamed its instance variable `discovery_rule_id`
  - Model `ServiceLevelResource` deleted or renamed its instance variable `service_level_objective_resource_id`
  - Model `UnifiedResilienceItemProperties` deleted or renamed its instance variable `recommendations`
  - Deleted or renamed enum value `UsagePlanType.BASIC`
  - Deleted or renamed model `GoalAssignmentType`
  - Deleted or renamed model `GoalTemplate`
  - Deleted or renamed model `GoalTemplateProperties`
  - Deleted or renamed model `GoalType`
  - Deleted or renamed model `MembershipType`
  - Deleted or renamed model `RecommendationsData`
  - Deleted or renamed model `RecommendationsHighAvailabilityData`
  - Deleted or renamed model `RequirementSelected`
  - Deleted or renamed model `ResilienceHealthStatus`
  - Deleted or renamed model `ServiceGroupMembership`
  - Deleted or renamed model `UnifiedResilienceItemRequirementSelected`
  - Deleted or renamed model `GoalTemplatesOperations`

## 1.0.0b2 (2026-09-23)

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
  - Model `DrillRunsOperations` added parameter `content_type` in method `begin_reprotect`
  - Model `DrillRunsOperations` added method `begin_generate_report`
  - Model `DrillRunsOperations` added method `begin_list_report_download_url`

### Breaking Changes

  - Model `DrillProperties` deleted or renamed its instance variable `managed_on_behalf_of_configuration`
  - Model `RegionalDrillProperties` deleted or renamed its instance variable `managed_on_behalf_of_configuration`
  - Model `ZonalDrillProperties` deleted or renamed its instance variable `managed_on_behalf_of_configuration`
  - Deleted or renamed model `ManagedOnBehalfOfConfiguration`
  - Deleted or renamed model `MoboBrokerResource`
  - Renamed model `UserConfirmationForHighAvailabilityItem` to `UserConfirmationItem`

## 1.0.0b1 (2026-06-16)

### Other Changes

  - Initial version
