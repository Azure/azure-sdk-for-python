# Release History

## 5.0.0b2 (2026-04-14)

### Features Added

  - Client `AuthorizationManagementClient` added parameter `cloud_setting` in method `__init__`
  - Client `AuthorizationManagementClient` added method `send_request`
  - Client `AuthorizationManagementClient` added operation group `attribute_namespaces`
  - Model `AccessReviewDecision` added property `properties`
  - Model `AccessReviewDecision` added property `system_data`
  - Model `AccessReviewDecisionInsight` added property `properties`
  - Model `AccessReviewDecisionProperties` added property `principal`
  - Model `AccessReviewDecisionProperties` added property `resource`
  - Model `AccessReviewDecisionProperties` added property `reviewed_by`
  - Model `AccessReviewDecisionProperties` added property `applied_by`
  - Model `AccessReviewDecisionProperties` added property `principal_resource_membership`
  - Model `AccessReviewDefaultSettings` added property `properties`
  - Model `AccessReviewDefaultSettings` added property `system_data`
  - Model `AccessReviewHistoryDefinition` added property `properties`
  - Model `AccessReviewHistoryDefinition` added property `system_data`
  - Model `AccessReviewHistoryDefinitionProperties` added property `created_by`
  - Model `AccessReviewHistoryDefinitionProperties` added property `settings`
  - Model `AccessReviewInstance` added property `properties`
  - Model `AccessReviewInstance` added property `system_data`
  - Model `AccessReviewScheduleDefinition` added property `properties`
  - Model `AccessReviewScheduleDefinition` added property `system_data`
  - Model `AccessReviewScheduleDefinitionProperties` added property `created_by`
  - Model `AccessReviewScheduleDefinitionProperties` added property `settings`
  - Model `AccessReviewScheduleDefinitionProperties` added property `scope`
  - Model `AccessReviewScheduleSettings` added property `recurrence`
  - Model `Alert` added property `system_data`
  - Model `AlertConfiguration` added property `properties`
  - Model `AlertConfiguration` added property `system_data`
  - Model `AlertDefinition` added property `system_data`
  - Model `AlertIncident` added property `properties`
  - Model `AlertIncident` added property `system_data`
  - Model `DenyAssignment` added property `system_data`
  - Model `RoleAssignment` added property `system_data`
  - Model `RoleAssignmentSchedule` added property `system_data`
  - Model `RoleAssignmentScheduleInstance` added property `system_data`
  - Model `RoleAssignmentScheduleRequest` added property `system_data`
  - Model `RoleDefinition` added property `system_data`
  - Model `RoleEligibilitySchedule` added property `system_data`
  - Model `RoleEligibilityScheduleInstance` added property `system_data`
  - Model `RoleEligibilityScheduleRequest` added property `system_data`
  - Model `RoleManagementPolicy` added property `system_data`
  - Model `RoleManagementPolicyAssignment` added property `system_data`
  - Added model `AccessReviewRecurrencePattern`
  - Added model `AccessReviewRecurrenceRange`
  - Added model `AttributeNamespace`
  - Added model `AttributeNamespaceCreateRequest`
  - Added model `CloudError`
  - Added enum `CommonUserType`
  - Added enum `CreatedByType`
  - Added enum `DenyAssignmentEffect`
  - Added model `DenyAssignmentPrincipal`
  - Added model `ExtensionResource`
  - Added model `ProxyResource`
  - Added model `Resource`
  - Added model `SettableResource`
  - Added model `SystemData`
  - Operation group `DenyAssignmentsOperations` added method `create_or_update`
  - Operation group `DenyAssignmentsOperations` added method `delete`
  - Added operation group `AttributeNamespacesOperations`

### Breaking Changes

  - This version introduces new hybrid models which have dual dictionary and model nature. Please follow https://aka.ms/azsdk/python/migrate/hybrid-models for migration.
  - For the method breakings, please refer to https://aka.ms/azsdk/python/migrate/operations for migration.
  - Model `AccessReviewDecision` moved instance variable `recommendation`, `decision`, `justification`, `reviewed_date_time`, `apply_result`, `applied_date_time`, `insights`, `membership_types`, `principal_id_properties_applied_by_principal_id`, `principal_type_properties_applied_by_principal_type`, `principal_name_properties_applied_by_principal_name`, `user_principal_name_properties_applied_by_user_principal_name`, `principal_id_properties_reviewed_by_principal_id`, `principal_type_properties_reviewed_by_principal_type`, `principal_name_properties_reviewed_by_principal_name`, `user_principal_name_properties_reviewed_by_user_principal_name`, `type_properties_resource_type`, `id_properties_resource_id`, `display_name_properties_resource_display_name`, `type_properties_principal_type`, `id_properties_principal_id` and `display_name_properties_principal_display_name` under property `properties` whose type is `AccessReviewDecisionProperties`
  - Model `AccessReviewDecisionInsight` moved instance variable `type_properties_type` and `insight_created_date_time` under property `properties` whose type is `AccessReviewDecisionInsightProperties`
  - Model `AccessReviewDecisionProperties` moved instance variable `membership_types` under property `principal_resource_membership` whose type is `AccessReviewDecisionPrincipalResourceMembership`
  - Model `AccessReviewDecisionProperties` moved instance variable `principal_id_applied_by_principal_id`, `principal_type_applied_by_principal_type`, `principal_name_applied_by_principal_name` and `user_principal_name_applied_by_user_principal_name` under property `applied_by` whose type is `AccessReviewActorIdentity`
  - Model `AccessReviewDecisionProperties` moved instance variable `principal_id_reviewed_by_principal_id`, `principal_type_reviewed_by_principal_type`, `principal_name_reviewed_by_principal_name` and `user_principal_name_reviewed_by_user_principal_name` under property `reviewed_by` whose type is `AccessReviewActorIdentity`
  - Model `AccessReviewDecisionProperties` moved instance variable `type_resource_type`, `id_resource_id` and `display_name_resource_display_name` under property `resource` whose type is `AccessReviewDecisionResource`
  - Model `AccessReviewDecisionProperties` moved instance variable `type_principal_type`, `id_principal_id` and `display_name_principal_display_name` under property `principal` whose type is `AccessReviewDecisionIdentity`
  - Model `AccessReviewDefaultSettings` moved instance variable `mail_notifications_enabled`, `reminder_notifications_enabled`, `default_decision_enabled`, `justification_required_on_approval`, `default_decision`, `auto_apply_decisions_enabled`, `recommendations_enabled`, `recommendation_look_back_duration`, `instance_duration_in_days`, `type_properties_recurrence_range_type`, `number_of_occurrences`, `start_date`, `end_date`, `type_properties_recurrence_pattern_type` and `interval` under property `properties` whose type is `AccessReviewScheduleSettings`
  - Model `AccessReviewHistoryDefinition` moved instance variable `display_name`, `review_history_period_start_date_time`, `review_history_period_end_date_time`, `decisions`, `status`, `created_date_time`, `scopes`, `instances`, `type_properties_settings_range_type`, `number_of_occurrences`, `start_date`, `end_date`, `type_properties_settings_pattern_type`, `interval`, `principal_id`, `principal_type`, `principal_name` and `user_principal_name` under property `properties` whose type is `AccessReviewHistoryDefinitionProperties`
  - Model `AccessReviewHistoryDefinitionProperties` moved instance variable `type_settings_range_type`, `number_of_occurrences`, `start_date`, `end_date`, `type_settings_pattern_type` and `interval` under property `settings` whose type is `AccessReviewHistoryScheduleSettings`
  - Model `AccessReviewHistoryDefinitionProperties` moved instance variable `principal_id`, `principal_type`, `principal_name` and `user_principal_name` under property `created_by` whose type is `AccessReviewActorIdentity`
  - Model `AccessReviewInstance` moved instance variable `status`, `start_date_time`, `end_date_time`, `reviewers`, `backup_reviewers` and `reviewers_type` under property `properties` whose type is `AccessReviewInstanceProperties`
  - Model `AccessReviewScheduleDefinition` moved instance variable `display_name`, `status`, `description_for_admins`, `description_for_reviewers`, `reviewers`, `backup_reviewers`, `reviewers_type`, `instances`, `resource_id`, `role_definition_id`, `principal_type_properties_scope_principal_type`, `assignment_state`, `inactive_duration`, `expand_nested_memberships`, `include_inherited_access`, `include_access_below_resource`, `exclude_resource_id`, `exclude_role_definition_id`, `mail_notifications_enabled`, `reminder_notifications_enabled`, `default_decision_enabled`, `justification_required_on_approval`, `default_decision`, `auto_apply_decisions_enabled`, `recommendations_enabled`, `recommendation_look_back_duration`, `instance_duration_in_days`, `type_properties_settings_recurrence_range_type`, `number_of_occurrences`, `start_date`, `end_date`, `type_properties_settings_recurrence_pattern_type`, `interval`, `principal_id`, `principal_type_properties_created_by_principal_type`, `principal_name` and `user_principal_name` under property `properties` whose type is `AccessReviewScheduleDefinitionProperties`
  - Model `AccessReviewScheduleDefinitionProperties` moved instance variable `resource_id`, `role_definition_id`, `principal_type_scope_principal_type`, `assignment_state`, `inactive_duration`, `expand_nested_memberships`, `include_inherited_access`, `include_access_below_resource`, `exclude_resource_id` and `exclude_role_definition_id` under property `scope` whose type is `AccessReviewScope`
  - Model `AccessReviewScheduleDefinitionProperties` moved instance variable `mail_notifications_enabled`, `reminder_notifications_enabled`, `default_decision_enabled`, `justification_required_on_approval`, `default_decision`, `auto_apply_decisions_enabled`, `recommendations_enabled`, `recommendation_look_back_duration`, `instance_duration_in_days`, `type_settings_recurrence_range_type`, `number_of_occurrences`, `start_date`, `end_date`, `type_settings_recurrence_pattern_type` and `interval` under property `settings` whose type is `AccessReviewScheduleSettings`
  - Model `AccessReviewScheduleDefinitionProperties` moved instance variable `principal_id`, `principal_type_created_by_principal_type`, `principal_name` and `user_principal_name` under property `created_by` whose type is `AccessReviewActorIdentity`
  - Model `AccessReviewScheduleSettings` moved instance variable `type_recurrence_range_type`, `number_of_occurrences`, `start_date`, `end_date`, `type_recurrence_pattern_type` and `interval` under property `recurrence` whose type is `AccessReviewRecurrenceSettings`
  - Model `AlertConfiguration` moved instance variable `alert_definition_id`, `scope`, `is_enabled`, `alert_configuration_type` and `alert_definition` under property `properties` whose type is `AlertConfigurationProperties`
  - Model `AlertIncident` moved instance variable `alert_incident_type` under property `properties` whose type is `AlertIncidentProperties`
  - Model `RoleAssignmentCreateParameters` moved instance variable `scope`, `role_definition_id`, `principal_id`, `principal_type`, `description`, `condition`, `condition_version`, `created_on`, `updated_on`, `created_by`, `updated_by` and `delegated_managed_identity_resource_id` under property `properties` whose type is `RoleAssignmentProperties`
  - Deleted model `ValidationResponse`
  - Deleted model `ValidationResponseErrorInfo`
  - Method `ProviderOperationsMetadataOperations.get` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `ProviderOperationsMetadataOperations.list` changed its parameter `expand` from `positional_or_keyword` to `keyword_only`
  - Method `RoleAssignmentsOperations.delete` changed its parameter `tenant_id` from `positional_or_keyword` to `keyword_only`
  - Method `RoleAssignmentsOperations.delete_by_id` changed its parameter `tenant_id` from `positional_or_keyword` to `keyword_only`
  - Method `RoleAssignmentsOperations.get` changed its parameter `tenant_id` from `positional_or_keyword` to `keyword_only`
  - Method `RoleAssignmentsOperations.get_by_id` changed its parameter `tenant_id` from `positional_or_keyword` to `keyword_only`
  - Method `RoleAssignmentsOperations.list_for_resource` changed its parameter `tenant_id` from `positional_or_keyword` to `keyword_only`
  - Method `RoleAssignmentsOperations.list_for_resource_group` changed its parameter `tenant_id` from `positional_or_keyword` to `keyword_only`
  - Method `RoleAssignmentsOperations.list_for_scope` changed its parameter `tenant_id`/`skip_token` from `positional_or_keyword` to `keyword_only`
  - Method `RoleAssignmentsOperations.list_for_subscription` changed its parameter `tenant_id` from `positional_or_keyword` to `keyword_only`

### Other Changes

  - Deleted model `DenyAssignmentFilter`/`PermissionGetResult`/`RoleAssignmentFilter`/`RoleAssignmentScheduleFilter`/`RoleAssignmentScheduleInstanceFilter`/`RoleAssignmentScheduleRequestFilter`/`RoleDefinitionFilter`/`RoleEligibilityScheduleFilter`/`RoleEligibilityScheduleInstanceFilter`/`RoleEligibilityScheduleRequestFilter` which actually were not used by SDK users

## 5.0.0b1 (2025-07-23)

### Features Added

  - Client `AuthorizationManagementClient` added operation group `classic_administrators`
  - Client `AuthorizationManagementClient` added operation group `global_administrator`
  - Client `AuthorizationManagementClient` added operation group `deny_assignments`
  - Client `AuthorizationManagementClient` added operation group `provider_operations_metadata`
  - Client `AuthorizationManagementClient` added operation group `role_assignments`
  - Client `AuthorizationManagementClient` added operation group `permissions`
  - Client `AuthorizationManagementClient` added operation group `role_definitions`
  - Client `AuthorizationManagementClient` added operation group `operations`
  - Client `AuthorizationManagementClient` added operation group `access_review_history_definitions`
  - Client `AuthorizationManagementClient` added operation group `access_review_history_definition`
  - Client `AuthorizationManagementClient` added operation group `access_review_history_definition_instance`
  - Client `AuthorizationManagementClient` added operation group `access_review_history_definition_instances`
  - Client `AuthorizationManagementClient` added operation group `access_review_schedule_definitions`
  - Client `AuthorizationManagementClient` added operation group `access_review_instances`
  - Client `AuthorizationManagementClient` added operation group `access_review_instance`
  - Client `AuthorizationManagementClient` added operation group `access_review_instance_decisions`
  - Client `AuthorizationManagementClient` added operation group `access_review_instance_contacted_reviewers`
  - Client `AuthorizationManagementClient` added operation group `access_review_default_settings`
  - Client `AuthorizationManagementClient` added operation group `scope_access_review_history_definitions`
  - Client `AuthorizationManagementClient` added operation group `scope_access_review_history_definition`
  - Client `AuthorizationManagementClient` added operation group `scope_access_review_history_definition_instance`
  - Client `AuthorizationManagementClient` added operation group `scope_access_review_history_definition_instances`
  - Client `AuthorizationManagementClient` added operation group `scope_access_review_schedule_definitions`
  - Client `AuthorizationManagementClient` added operation group `scope_access_review_instances`
  - Client `AuthorizationManagementClient` added operation group `scope_access_review_instance`
  - Client `AuthorizationManagementClient` added operation group `scope_access_review_instance_decisions`
  - Client `AuthorizationManagementClient` added operation group `scope_access_review_instance_contacted_reviewers`
  - Client `AuthorizationManagementClient` added operation group `scope_access_review_default_settings`
  - Client `AuthorizationManagementClient` added operation group `access_review_schedule_definitions_assigned_for_my_approval`
  - Client `AuthorizationManagementClient` added operation group `access_review_instances_assigned_for_my_approval`
  - Client `AuthorizationManagementClient` added operation group `access_review_instance_my_decisions`
  - Client `AuthorizationManagementClient` added operation group `tenant_level_access_review_instance_contacted_reviewers`
  - Client `AuthorizationManagementClient` added operation group `eligible_child_resources`
  - Client `AuthorizationManagementClient` added operation group `role_assignment_schedules`
  - Client `AuthorizationManagementClient` added operation group `role_assignment_schedule_instances`
  - Client `AuthorizationManagementClient` added operation group `role_assignment_schedule_requests`
  - Client `AuthorizationManagementClient` added operation group `role_eligibility_schedules`
  - Client `AuthorizationManagementClient` added operation group `role_eligibility_schedule_instances`
  - Client `AuthorizationManagementClient` added operation group `role_eligibility_schedule_requests`
  - Client `AuthorizationManagementClient` added operation group `role_management_policies`
  - Client `AuthorizationManagementClient` added operation group `role_management_policy_assignments`
  - Added enum `AccessRecommendationType`
  - Added enum `AccessReviewActorIdentityType`
  - Added enum `AccessReviewApplyResult`
  - Added model `AccessReviewContactedReviewer`
  - Added model `AccessReviewContactedReviewerListResult`
  - Added model `AccessReviewDecision`
  - Added model `AccessReviewDecisionIdentity`
  - Added model `AccessReviewDecisionInsight`
  - Added model `AccessReviewDecisionInsightProperties`
  - Added enum `AccessReviewDecisionInsightType`
  - Added model `AccessReviewDecisionListResult`
  - Added enum `AccessReviewDecisionPrincipalResourceMembershipType`
  - Added model `AccessReviewDecisionProperties`
  - Added model `AccessReviewDecisionServicePrincipalIdentity`
  - Added model `AccessReviewDecisionUserIdentity`
  - Added model `AccessReviewDecisionUserSignInInsightProperties`
  - Added model `AccessReviewDefaultSettings`
  - Added model `AccessReviewHistoryDefinition`
  - Added model `AccessReviewHistoryDefinitionInstanceListResult`
  - Added model `AccessReviewHistoryDefinitionListResult`
  - Added model `AccessReviewHistoryDefinitionProperties`
  - Added enum `AccessReviewHistoryDefinitionStatus`
  - Added model `AccessReviewHistoryInstance`
  - Added model `AccessReviewInstance`
  - Added model `AccessReviewInstanceListResult`
  - Added model `AccessReviewInstanceProperties`
  - Added enum `AccessReviewInstanceReviewersType`
  - Added enum `AccessReviewInstanceStatus`
  - Added enum `AccessReviewRecurrencePatternType`
  - Added enum `AccessReviewRecurrenceRangeType`
  - Added enum `AccessReviewResult`
  - Added model `AccessReviewReviewer`
  - Added enum `AccessReviewReviewerType`
  - Added model `AccessReviewScheduleDefinition`
  - Added model `AccessReviewScheduleDefinitionListResult`
  - Added model `AccessReviewScheduleDefinitionProperties`
  - Added enum `AccessReviewScheduleDefinitionReviewersType`
  - Added enum `AccessReviewScheduleDefinitionStatus`
  - Added model `AccessReviewScheduleSettings`
  - Added model `AccessReviewScope`
  - Added enum `AccessReviewScopeAssignmentState`
  - Added enum `AccessReviewScopePrincipalType`
  - Added enum `ApprovalMode`
  - Added model `ApprovalSettings`
  - Added model `ApprovalStage`
  - Added enum `AssignmentType`
  - Added model `ClassicAdministrator`
  - Added model `ClassicAdministratorListResult`
  - Added enum `DecisionResourceType`
  - Added enum `DecisionTargetType`
  - Added enum `DefaultDecisionType`
  - Added model `DenyAssignment`
  - Added model `DenyAssignmentFilter`
  - Added model `DenyAssignmentListResult`
  - Added model `DenyAssignmentPermission`
  - Added model `EligibleChildResource`
  - Added model `EligibleChildResourcesListResult`
  - Added enum `EnablementRules`
  - Added model `ErrorAdditionalInfo`
  - Added model `ErrorDefinition`
  - Added model `ErrorDefinitionProperties`
  - Added model `ErrorDetail`
  - Added model `ErrorResponse`
  - Added enum `ExcludedPrincipalTypes`
  - Added model `ExpandedProperties`
  - Added model `ExpandedPropertiesPrincipal`
  - Added model `ExpandedPropertiesRoleDefinition`
  - Added model `ExpandedPropertiesScope`
  - Added enum `MemberType`
  - Added enum `NotificationDeliveryMechanism`
  - Added enum `NotificationLevel`
  - Added model `Operation`
  - Added model `OperationDisplay`
  - Added model `OperationListResult`
  - Added enum `PIMOnlyMode`
  - Added model `PIMOnlyModeSettings`
  - Added model `Permission`
  - Added model `PermissionGetResult`
  - Added model `PolicyAssignmentProperties`
  - Added model `PolicyAssignmentPropertiesPolicy`
  - Added model `PolicyAssignmentPropertiesRoleDefinition`
  - Added model `PolicyAssignmentPropertiesScope`
  - Added model `PolicyProperties`
  - Added model `PolicyPropertiesScope`
  - Added model `Principal`
  - Added enum `PrincipalType`
  - Added model `ProviderOperation`
  - Added model `ProviderOperationsMetadata`
  - Added model `ProviderOperationsMetadataListResult`
  - Added enum `RecipientType`
  - Added model `RecordAllDecisionsProperties`
  - Added enum `RecordAllDecisionsResult`
  - Added enum `RequestType`
  - Added model `ResourceType`
  - Added model `RoleAssignment`
  - Added model `RoleAssignmentCreateParameters`
  - Added model `RoleAssignmentFilter`
  - Added model `RoleAssignmentListResult`
  - Added model `RoleAssignmentSchedule`
  - Added model `RoleAssignmentScheduleFilter`
  - Added model `RoleAssignmentScheduleInstance`
  - Added model `RoleAssignmentScheduleInstanceFilter`
  - Added model `RoleAssignmentScheduleInstanceListResult`
  - Added model `RoleAssignmentScheduleListResult`
  - Added model `RoleAssignmentScheduleRequest`
  - Added model `RoleAssignmentScheduleRequestFilter`
  - Added model `RoleAssignmentScheduleRequestListResult`
  - Added model `RoleAssignmentScheduleRequestPropertiesScheduleInfo`
  - Added model `RoleAssignmentScheduleRequestPropertiesScheduleInfoExpiration`
  - Added model `RoleAssignmentScheduleRequestPropertiesTicketInfo`
  - Added model `RoleDefinition`
  - Added model `RoleDefinitionFilter`
  - Added model `RoleDefinitionListResult`
  - Added model `RoleEligibilitySchedule`
  - Added model `RoleEligibilityScheduleFilter`
  - Added model `RoleEligibilityScheduleInstance`
  - Added model `RoleEligibilityScheduleInstanceFilter`
  - Added model `RoleEligibilityScheduleInstanceListResult`
  - Added model `RoleEligibilityScheduleListResult`
  - Added model `RoleEligibilityScheduleRequest`
  - Added model `RoleEligibilityScheduleRequestFilter`
  - Added model `RoleEligibilityScheduleRequestListResult`
  - Added model `RoleEligibilityScheduleRequestPropertiesScheduleInfo`
  - Added model `RoleEligibilityScheduleRequestPropertiesScheduleInfoExpiration`
  - Added model `RoleEligibilityScheduleRequestPropertiesTicketInfo`
  - Added model `RoleManagementPolicy`
  - Added model `RoleManagementPolicyApprovalRule`
  - Added model `RoleManagementPolicyAssignment`
  - Added model `RoleManagementPolicyAssignmentListResult`
  - Added model `RoleManagementPolicyAuthenticationContextRule`
  - Added model `RoleManagementPolicyEnablementRule`
  - Added model `RoleManagementPolicyExpirationRule`
  - Added model `RoleManagementPolicyListResult`
  - Added model `RoleManagementPolicyNotificationRule`
  - Added model `RoleManagementPolicyPimOnlyModeRule`
  - Added model `RoleManagementPolicyRule`
  - Added model `RoleManagementPolicyRuleTarget`
  - Added enum `RoleManagementPolicyRuleType`
  - Added enum `Status`
  - Added enum `Type`
  - Added model `UserSet`
  - Added enum `UserType`
  - Added model `UsersOrServicePrincipalSet`
  - Added model `ValidationResponse`
  - Added model `ValidationResponseErrorInfo`
  - Added model `AccessReviewDefaultSettingsOperations`
  - Added model `AccessReviewHistoryDefinitionInstanceOperations`
  - Added model `AccessReviewHistoryDefinitionInstancesOperations`
  - Added model `AccessReviewHistoryDefinitionOperations`
  - Added model `AccessReviewHistoryDefinitionsOperations`
  - Added model `AccessReviewInstanceContactedReviewersOperations`
  - Added model `AccessReviewInstanceDecisionsOperations`
  - Added model `AccessReviewInstanceMyDecisionsOperations`
  - Added model `AccessReviewInstanceOperations`
  - Added model `AccessReviewInstancesAssignedForMyApprovalOperations`
  - Added model `AccessReviewInstancesOperations`
  - Added model `AccessReviewScheduleDefinitionsAssignedForMyApprovalOperations`
  - Added model `AccessReviewScheduleDefinitionsOperations`
  - Added model `ClassicAdministratorsOperations`
  - Added model `DenyAssignmentsOperations`
  - Added model `EligibleChildResourcesOperations`
  - Added model `GlobalAdministratorOperations`
  - Added model `Operations`
  - Added model `PermissionsOperations`
  - Added model `ProviderOperationsMetadataOperations`
  - Added model `RoleAssignmentScheduleInstancesOperations`
  - Added model `RoleAssignmentScheduleRequestsOperations`
  - Added model `RoleAssignmentSchedulesOperations`
  - Added model `RoleAssignmentsOperations`
  - Added model `RoleDefinitionsOperations`
  - Added model `RoleEligibilityScheduleInstancesOperations`
  - Added model `RoleEligibilityScheduleRequestsOperations`
  - Added model `RoleEligibilitySchedulesOperations`
  - Added model `RoleManagementPoliciesOperations`
  - Added model `RoleManagementPolicyAssignmentsOperations`
  - Added model `ScopeAccessReviewDefaultSettingsOperations`
  - Added model `ScopeAccessReviewHistoryDefinitionInstanceOperations`
  - Added model `ScopeAccessReviewHistoryDefinitionInstancesOperations`
  - Added model `ScopeAccessReviewHistoryDefinitionOperations`
  - Added model `ScopeAccessReviewHistoryDefinitionsOperations`
  - Added model `ScopeAccessReviewInstanceContactedReviewersOperations`
  - Added model `ScopeAccessReviewInstanceDecisionsOperations`
  - Added model `ScopeAccessReviewInstanceOperations`
  - Added model `ScopeAccessReviewInstancesOperations`
  - Added model `ScopeAccessReviewScheduleDefinitionsOperations`
  - Added model `TenantLevelAccessReviewInstanceContactedReviewersOperations`

### Breaking Changes

  - This package now only targets the latest Api-Version available on Azure and removes APIs of other Api-Version. After this change, the package can have much smaller size. If your application requires a specific and non-latest Api-Version, it's recommended to pin this package to the previous released version; If your application always only use latest Api-Version, please ignore this change.

## 4.0.0 (2023-07-21)

### Features Added

  - Added operation RoleAssignmentScheduleRequestsOperations.validate
  - Added operation RoleEligibilityScheduleRequestsOperations.validate
  - Model AlertConfiguration has a new parameter alert_definition
  - Model AlertConfigurationProperties has a new parameter alert_definition
  - Model AlertOperationResult has a new parameter created_date_time
  - Model AlertOperationResult has a new parameter last_action_date_time
  - Model AlertOperationResult has a new parameter resource_location
  - Model AlertOperationResult has a new parameter status_detail
  - Model AzureRolesAssignedOutsidePimAlertConfigurationProperties has a new parameter alert_definition
  - Model DenyAssignment has a new parameter condition
  - Model DenyAssignment has a new parameter condition_version
  - Model DenyAssignment has a new parameter created_by
  - Model DenyAssignment has a new parameter created_on
  - Model DenyAssignment has a new parameter updated_by
  - Model DenyAssignment has a new parameter updated_on
  - Model DuplicateRoleCreatedAlertConfigurationProperties has a new parameter alert_definition
  - Model Permission has a new parameter condition
  - Model Permission has a new parameter condition_version
  - Model RoleDefinition has a new parameter created_by
  - Model RoleDefinition has a new parameter created_on
  - Model RoleDefinition has a new parameter updated_by
  - Model RoleDefinition has a new parameter updated_on
  - Model TooManyOwnersAssignedToResourceAlertConfigurationProperties has a new parameter alert_definition
  - Model TooManyPermanentOwnersAssignedToResourceAlertConfigurationProperties has a new parameter alert_definition

### Breaking Changes

  - Removed operation AlertOperationOperations.list_for_scope

## 3.1.0b1 (2023-02-15)

### Features Added

  - Model AlertConfiguration has a new parameter alert_definition
  - Model AlertConfigurationProperties has a new parameter alert_definition
  - Model AzureRolesAssignedOutsidePimAlertConfigurationProperties has a new parameter alert_definition
  - Model DenyAssignment has a new parameter condition
  - Model DenyAssignment has a new parameter condition_version
  - Model DenyAssignment has a new parameter created_by
  - Model DenyAssignment has a new parameter created_on
  - Model DenyAssignment has a new parameter updated_by
  - Model DenyAssignment has a new parameter updated_on
  - Model DuplicateRoleCreatedAlertConfigurationProperties has a new parameter alert_definition
  - Model RoleDefinition has a new parameter created_by
  - Model RoleDefinition has a new parameter created_on
  - Model RoleDefinition has a new parameter updated_by
  - Model RoleDefinition has a new parameter updated_on
  - Model TooManyOwnersAssignedToResourceAlertConfigurationProperties has a new parameter alert_definition
  - Model TooManyPermanentOwnersAssignedToResourceAlertConfigurationProperties has a new parameter alert_definition

## 3.0.0 (2022-10-11)

### Features Added

  - Added operation AccessReviewInstancesOperations.create
  - Added operation group AccessReviewHistoryDefinitionInstanceOperations
  - Added operation group AccessReviewHistoryDefinitionInstancesOperations
  - Added operation group AccessReviewHistoryDefinitionOperations
  - Added operation group AccessReviewHistoryDefinitionsOperations
  - Added operation group AccessReviewInstanceContactedReviewersOperations
  - Added operation group AlertConfigurationsOperations
  - Added operation group AlertDefinitionsOperations
  - Added operation group AlertIncidentsOperations
  - Added operation group AlertOperationOperations
  - Added operation group AlertsOperations
  - Added operation group ScopeAccessReviewDefaultSettingsOperations
  - Added operation group ScopeAccessReviewHistoryDefinitionInstanceOperations
  - Added operation group ScopeAccessReviewHistoryDefinitionInstancesOperations
  - Added operation group ScopeAccessReviewHistoryDefinitionOperations
  - Added operation group ScopeAccessReviewHistoryDefinitionsOperations
  - Added operation group ScopeAccessReviewInstanceContactedReviewersOperations
  - Added operation group ScopeAccessReviewInstanceDecisionsOperations
  - Added operation group ScopeAccessReviewInstanceOperations
  - Added operation group ScopeAccessReviewInstancesOperations
  - Added operation group ScopeAccessReviewScheduleDefinitionsOperations
  - Added operation group TenantLevelAccessReviewInstanceContactedReviewersOperations
  - Model AccessReviewDecision has a new parameter insights
  - Model AccessReviewDecision has a new parameter membership_types
  - Model AccessReviewDecisionProperties has a new parameter insights
  - Model AccessReviewDecisionProperties has a new parameter membership_types
  - Model AccessReviewDefaultSettings has a new parameter recommendation_look_back_duration
  - Model AccessReviewInstance has a new parameter backup_reviewers
  - Model AccessReviewInstance has a new parameter reviewers
  - Model AccessReviewInstance has a new parameter reviewers_type
  - Model AccessReviewScheduleDefinition has a new parameter exclude_resource_id
  - Model AccessReviewScheduleDefinition has a new parameter exclude_role_definition_id
  - Model AccessReviewScheduleDefinition has a new parameter expand_nested_memberships
  - Model AccessReviewScheduleDefinition has a new parameter include_access_below_resource
  - Model AccessReviewScheduleDefinition has a new parameter include_inherited_access
  - Model AccessReviewScheduleDefinition has a new parameter recommendation_look_back_duration
  - Model AccessReviewScheduleDefinitionProperties has a new parameter exclude_resource_id
  - Model AccessReviewScheduleDefinitionProperties has a new parameter exclude_role_definition_id
  - Model AccessReviewScheduleDefinitionProperties has a new parameter expand_nested_memberships
  - Model AccessReviewScheduleDefinitionProperties has a new parameter include_access_below_resource
  - Model AccessReviewScheduleDefinitionProperties has a new parameter include_inherited_access
  - Model AccessReviewScheduleDefinitionProperties has a new parameter recommendation_look_back_duration
  - Model AccessReviewScheduleSettings has a new parameter recommendation_look_back_duration
  - Model DenyAssignmentPermission has a new parameter condition
  - Model DenyAssignmentPermission has a new parameter condition_version

### Breaking Changes

  - Operation RoleAssignmentsOperations.list_for_scope has a new parameter skip_token
  - Removed operation RoleAssignmentsOperations.validate
  - Removed operation RoleAssignmentsOperations.validate_by_id

## 2.0.0 (2021-09-26)

**Features**

  - Model RoleAssignment has a new parameter created_on
  - Model RoleAssignment has a new parameter delegated_managed_identity_resource_id
  - Model RoleAssignment has a new parameter updated_by
  - Model RoleAssignment has a new parameter condition
  - Model RoleAssignment has a new parameter description
  - Model RoleAssignment has a new parameter updated_on
  - Model RoleAssignment has a new parameter condition_version
  - Model RoleAssignment has a new parameter created_by
  - Added operation RoleAssignmentsOperations.validate
  - Added operation RoleAssignmentsOperations.list_for_subscription
  - Added operation RoleAssignmentsOperations.validate_by_id
  - Added operation RoleAssignmentsOperations.create_by_id
  - Added operation RoleAssignmentsOperations.get_by_id
  - Added operation RoleAssignmentsOperations.delete_by_id
  - Added operation group AccessReviewInstancesAssignedForMyApprovalOperations
  - Added operation group RoleManagementPolicyAssignmentsOperations
  - Added operation group EligibleChildResourcesOperations
  - Added operation group AccessReviewInstanceDecisionsOperations
  - Added operation group RoleAssignmentSchedulesOperations
  - Added operation group RoleEligibilityScheduleRequestsOperations
  - Added operation group RoleEligibilitySchedulesOperations
  - Added operation group RoleAssignmentScheduleInstancesOperations
  - Added operation group AccessReviewInstanceMyDecisionsOperations
  - Added operation group RoleAssignmentApprovalStepOperations
  - Added operation group AccessReviewInstancesOperations
  - Added operation group AccessReviewScheduleDefinitionsOperations
  - Added operation group ScopeRoleAssignmentApprovalOperations
  - Added operation group RoleAssignmentScheduleRequestsOperations
  - Added operation group RoleAssignmentApprovalStepsOperations
  - Added operation group RoleAssignmentApprovalOperations
  - Added operation group ScopeRoleAssignmentApprovalStepsOperations
  - Added operation group AccessReviewDefaultSettingsOperations
  - Added operation group RoleEligibilityScheduleInstancesOperations
  - Added operation group AccessReviewScheduleDefinitionsAssignedForMyApprovalOperations
  - Added operation group ScopeRoleAssignmentApprovalStepOperations
  - Added operation group RoleAssignmentMetricsOperations
  - Added operation group RoleManagementPoliciesOperations
  - Added operation group Operations
  - Added operation group AccessReviewInstanceOperations

**Breaking changes**

  - Operation RoleAssignmentsOperations.list_for_resource has a new signature
  - Operation RoleAssignmentsOperations.delete has a new signature
  - Operation RoleAssignmentsOperations.get has a new signature
  - Operation RoleAssignmentsOperations.list_for_resource has a new signature
  - Operation RoleAssignmentsOperations.list_for_resource_group has a new signature
  - Operation RoleAssignmentsOperations.list_for_scope has a new signature
  - Model RoleAssignmentFilter no longer has parameter can_delegate
  - Model RoleAssignment no longer has parameter can_delegate
  - Model Principal has a new signature
  - Model RoleAssignmentCreateParameters has a new signature
  - Removed operation RoleAssignmentsOperations.list

## 1.0.0 (2020-11-23)

## 1.0.0b1 (2020-10-13)

This is beta preview version.

This version uses a next-generation code generator that introduces important breaking changes, but also important new features (like unified authentication and async programming).

**General breaking changes**

- Credential system has been completly revamped:

  - `azure.common.credentials` or `msrestazure.azure_active_directory` instances are no longer supported, use the `azure-identity` classes instead: https://pypi.org/project/azure-identity/
  - `credentials` parameter has been renamed `credential`

- The `config` attribute no longer exists on a client, configuration should be passed as kwarg. Example: `MyClient(credential, subscription_id, enable_logging=True)`. For a complete set of
  supported options, see the [parameters accept in init documentation of azure-core](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/CLIENT_LIBRARY_DEVELOPER.md#available-policies)
- You can't import a `version` module anymore, use `__version__` instead
- Operations that used to return a `msrest.polling.LROPoller` now returns a `azure.core.polling.LROPoller` and are prefixed with `begin_`.
- Exceptions tree have been simplified and most exceptions are now `azure.core.exceptions.HttpResponseError` (`CloudError` has been removed).
- Most of the operation kwarg have changed. Some of the most noticeable:

  - `raw` has been removed. Equivalent feature can be found using `cls`, a callback that will give access to internal HTTP response for advanced user
  - For a complete set of
  supported options, see the [parameters accept in Request documentation of azure-core](https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/core/azure-core/CLIENT_LIBRARY_DEVELOPER.md#available-policies)

**General new features**

- Type annotations support using `typing`. SDKs are mypy ready.
- This client has now stable and official support for async. Check the `aio` namespace of your package to find the async client.
- This client now support natively tracing library like OpenCensus or OpenTelemetry. See this [tracing quickstart](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/core/azure-core-tracing-opentelemetry) for an overview.

## 0.61.0 (2020-08-10)

**Features**

  - Model RoleAssignmentCreateParameters has a new parameter condition
  - Model RoleAssignmentCreateParameters has a new parameter description
  - Model RoleAssignmentCreateParameters has a new parameter condition_version
  - Model RoleAssignment has a new parameter condition
  - Model RoleAssignment has a new parameter description
  - Model RoleAssignment has a new parameter condition_version

## 0.60.0 (2019-06-25)

**Breaking changes**

  - Rename elevate_access.post to global_administrator.elevate_access

**General Breaking changes**

This version uses a next-generation code generator that *might*
introduce breaking changes if you were importing from the v20xx_yy_zz
API folders. In summary, some modules were incorrectly
visible/importable and have been renamed. This fixed several issues
caused by usage of classes that were not supposed to be used in the
first place.

  - AuthorizationManagementClient cannot be imported from
    `azure.mgmt.authorization.v20xx_yy_zz.authorization_management_client`
    anymore (import from `azure.mgmt.authorization.v20xx_yy_zz`
    works like before)
  - AuthorizationManagementClientConfiguration import has been moved
    from
    `azure.mgmt.authorization.v20xx_yy_zz.authorization_management_client`
    to `azure.mgmt.authorization.v20xx_yy_zz`
  - A model `MyClass` from a "models" sub-module cannot be imported
    anymore using
    `azure.mgmt.authorization.v20xx_yy_zz.models.my_class` (import
    from `azure.mgmt.authorization.v20xx_yy_zz.models` works like
    before)
  - An operation class `MyClassOperations` from an `operations`
    sub-module cannot be imported anymore using
    `azure.mgmt.authorization.v20xx_yy_zz.operations.my_class_operations`
    (import from `azure.mgmt.authorization.v20xx_yy_zz.operations`
    works like before)

Last but not least, HTTP connection pooling is now enabled by default.
You should always use a client as a context manager, or call close(), or
use no more than one client per process.

## 0.52.0 (2019-05-23)

**Features**

  - Add elevate_access API

## 0.51.1 (2018-11-27)

**Bugfixes**

  - Missing principal_type in role assignment class #3802

## 0.51.0 (2018-11-12)

**Features**

  - Model RoleAssignmentCreateParameters has a new parameter
    principal_type

**Breaking changes**

  - Parameter role_definition_id of model
    RoleAssignmentCreateParameters is now required
  - Parameter principal_id of model RoleAssignmentCreateParameters is
    now required

Role Assignments API version is now 2018-09-01-preview

## 0.50.0 (2018-05-29)

**Features**

  - Support Azure Stack (multi API versionning)
  - Client class can be used as a context manager to keep the underlying
    HTTP session open for performance

**Bugfixes**

  - Compatibility of the sdist with wheel 0.31.0

## 0.40.0 (2018-03-13)

**Breaking changes**

  - Several properties have been flattened and "properties" attribute is
    not needed anymore (e.g. properties.email_address =>
    email_address)
  - Some method signature change (e.g. create_by_id)

**Features**

  - Adding attributes data_actions / not_data_actions /
    is_data_actions

API version is now 2018-01-01-preview

## 0.30.0 (2017-04-28)

  - Initial Release
  - This wheel package is built with the azure wheel extension
