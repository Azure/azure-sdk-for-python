# Release History

## 2.0.0b2 (2022-12-27)

### Features Added

  - Added operation group GetOperations
  - Added operation group GetRecommendationsOperations
  - Added operation group IncidentTasksOperations
  - Added operation group UpdateOperations
  - Model AlertDetailsOverride has a new parameter alert_dynamic_properties
  - Model NrtAlertRule has a new parameter sentinel_entities_mappings
  - Model NrtAlertRuleTemplate has a new parameter sentinel_entities_mappings
  - Model NrtAlertRuleTemplateProperties has a new parameter sentinel_entities_mappings
  - Model QueryBasedAlertRuleTemplateProperties has a new parameter sentinel_entities_mappings
  - Model ScheduledAlertRule has a new parameter sentinel_entities_mappings
  - Model ScheduledAlertRuleCommonProperties has a new parameter sentinel_entities_mappings
  - Model ScheduledAlertRuleProperties has a new parameter sentinel_entities_mappings
  - Model ScheduledAlertRuleTemplate has a new parameter sentinel_entities_mappings
  - Model SecurityAlertTimelineItem has a new parameter intent
  - Model SecurityAlertTimelineItem has a new parameter techniques

## 2.0.0b1 (2022-09-29)

### Features Added

  - Added operation DataConnectorsOperations.connect
  - Added operation DataConnectorsOperations.disconnect
  - Added operation IncidentsOperations.create_team
  - Added operation IncidentsOperations.run_playbook
  - Added operation group BookmarkOperations
  - Added operation group BookmarkRelationsOperations
  - Added operation group DataConnectorsCheckRequirementsOperations
  - Added operation group DomainWhoisOperations
  - Added operation group EntitiesGetTimelineOperations
  - Added operation group EntitiesOperations
  - Added operation group EntitiesRelationsOperations
  - Added operation group EntityQueriesOperations
  - Added operation group EntityQueryTemplatesOperations
  - Added operation group EntityRelationsOperations
  - Added operation group FileImportsOperations
  - Added operation group IPGeodataOperations
  - Added operation group MetadataOperations
  - Added operation group OfficeConsentsOperations
  - Added operation group ProductSettingsOperations
  - Added operation group SecurityMLAnalyticsSettingsOperations
  - Added operation group SourceControlOperations
  - Added operation group SourceControlsOperations
  - Model Bookmark has a new parameter entity_mappings
  - Model Bookmark has a new parameter tactics
  - Model Bookmark has a new parameter techniques
  - Model FusionAlertRule has a new parameter scenario_exclusion_patterns
  - Model FusionAlertRule has a new parameter source_settings
  - Model FusionAlertRule has a new parameter techniques
  - Model FusionAlertRuleTemplate has a new parameter source_settings
  - Model FusionAlertRuleTemplate has a new parameter techniques
  - Model Incident has a new parameter provider_incident_id
  - Model Incident has a new parameter provider_name
  - Model Incident has a new parameter team_information
  - Model IncidentAdditionalData has a new parameter provider_incident_url
  - Model IncidentAdditionalData has a new parameter techniques
  - Model IncidentOwnerInfo has a new parameter owner_type
  - Model IoTDeviceEntity has a new parameter device_sub_type
  - Model IoTDeviceEntity has a new parameter importance
  - Model IoTDeviceEntity has a new parameter is_authorized
  - Model IoTDeviceEntity has a new parameter is_programming
  - Model IoTDeviceEntity has a new parameter is_scanner
  - Model IoTDeviceEntity has a new parameter nic_entity_ids
  - Model IoTDeviceEntity has a new parameter owners
  - Model IoTDeviceEntity has a new parameter purdue_layer
  - Model IoTDeviceEntity has a new parameter sensor
  - Model IoTDeviceEntity has a new parameter site
  - Model IoTDeviceEntity has a new parameter zone
  - Model IoTDeviceEntityProperties has a new parameter device_sub_type
  - Model IoTDeviceEntityProperties has a new parameter importance
  - Model IoTDeviceEntityProperties has a new parameter is_authorized
  - Model IoTDeviceEntityProperties has a new parameter is_programming
  - Model IoTDeviceEntityProperties has a new parameter is_scanner
  - Model IoTDeviceEntityProperties has a new parameter nic_entity_ids
  - Model IoTDeviceEntityProperties has a new parameter owners
  - Model IoTDeviceEntityProperties has a new parameter purdue_layer
  - Model IoTDeviceEntityProperties has a new parameter sensor
  - Model IoTDeviceEntityProperties has a new parameter site
  - Model IoTDeviceEntityProperties has a new parameter zone
  - Model ScheduledAlertRule has a new parameter techniques
  - Model ScheduledAlertRuleProperties has a new parameter techniques
  - Model ScheduledAlertRuleTemplate has a new parameter techniques
  - Model Watchlist has a new parameter source_type

### Breaking Changes

  - Parameter alerts of model AlertsDataTypeOfDataConnector is now required
  - Parameter alerts of model MCASDataConnectorDataTypes is now required
  - Parameter exchange of model OfficeDataConnectorDataTypes is now required
  - Parameter indicators of model TIDataConnectorDataTypes is now required
  - Parameter logs of model AwsCloudTrailDataConnectorDataTypes is now required
  - Parameter share_point of model OfficeDataConnectorDataTypes is now required
  - Parameter state of model AwsCloudTrailDataConnectorDataTypesLogs is now required
  - Parameter state of model DataConnectorDataTypeCommon is now required
  - Parameter state of model OfficeDataConnectorDataTypesExchange is now required
  - Parameter state of model OfficeDataConnectorDataTypesSharePoint is now required
  - Parameter state of model OfficeDataConnectorDataTypesTeams is now required
  - Parameter state of model TIDataConnectorDataTypesIndicators is now required
  - Parameter teams of model OfficeDataConnectorDataTypes is now required
  - Parameter tenant_id of model DataConnectorTenantId is now required

## 1.0.0 (2022-07-26)

**Breaking changes**

  - Model Bookmark no longer has parameter entity_mappings
  - Model Bookmark no longer has parameter tactics
  - Model Bookmark no longer has parameter techniques
  - Model FusionAlertRule no longer has parameter scenario_exclusion_patterns
  - Model FusionAlertRule no longer has parameter source_settings
  - Model FusionAlertRule no longer has parameter techniques
  - Model FusionAlertRuleTemplate no longer has parameter source_settings
  - Model FusionAlertRuleTemplate no longer has parameter techniques
  - Model Incident no longer has parameter provider_incident_id
  - Model Incident no longer has parameter provider_name
  - Model Incident no longer has parameter team_information
  - Model IncidentAdditionalData no longer has parameter provider_incident_url
  - Model IncidentAdditionalData no longer has parameter techniques
  - Model IncidentOwnerInfo no longer has parameter owner_type
  - Model ScheduledAlertRule no longer has parameter techniques
  - Model ScheduledAlertRuleProperties no longer has parameter techniques
  - Model ScheduledAlertRuleTemplate no longer has parameter techniques
  - Model Watchlist no longer has parameter source_type
  - Parameter logic_app_resource_id of model PlaybookActionProperties is now required
  - Removed operation DataConnectorsOperations.connect
  - Removed operation DataConnectorsOperations.disconnect
  - Removed operation IncidentsOperations.create_team
  - Removed operation IncidentsOperations.run_playbook
  - Removed operation group BookmarkOperations
  - Removed operation group BookmarkRelationsOperations
  - Removed operation group DataConnectorsCheckRequirementsOperations
  - Removed operation group DomainWhoisOperations
  - Removed operation group EntitiesGetTimelineOperations
  - Removed operation group EntitiesOperations
  - Removed operation group EntitiesRelationsOperations
  - Removed operation group EntityQueriesOperations
  - Removed operation group EntityQueryTemplatesOperations
  - Removed operation group EntityRelationsOperations
  - Removed operation group IPGeodataOperations
  - Removed operation group MetadataOperations
  - Removed operation group OfficeConsentsOperations
  - Removed operation group ProductSettingsOperations
  - Removed operation group SourceControlOperations
  - Removed operation group SourceControlsOperations

## 1.0.0b2 (2022-03-30)

**Features**

  - Added operation ActionsOperations.create_or_update
  - Added operation ActionsOperations.delete
  - Added operation ActionsOperations.get
  - Added operation DataConnectorsOperations.connect
  - Added operation DataConnectorsOperations.disconnect
  - Added operation IncidentCommentsOperations.create_or_update
  - Added operation IncidentCommentsOperations.delete
  - Added operation IncidentCommentsOperations.list
  - Added operation IncidentsOperations.create_team
  - Added operation IncidentsOperations.list_alerts
  - Added operation IncidentsOperations.list_bookmarks
  - Added operation IncidentsOperations.list_entities
  - Added operation IncidentsOperations.run_playbook
  - Added operation group AutomationRulesOperations
  - Added operation group BookmarkOperations
  - Added operation group BookmarkRelationsOperations
  - Added operation group DataConnectorsCheckRequirementsOperations
  - Added operation group DomainWhoisOperations
  - Added operation group EntitiesGetTimelineOperations
  - Added operation group EntitiesOperations
  - Added operation group EntitiesRelationsOperations
  - Added operation group EntityQueriesOperations
  - Added operation group EntityQueryTemplatesOperations
  - Added operation group EntityRelationsOperations
  - Added operation group IPGeodataOperations
  - Added operation group IncidentRelationsOperations
  - Added operation group MetadataOperations
  - Added operation group OfficeConsentsOperations
  - Added operation group ProductSettingsOperations
  - Added operation group SentinelOnboardingStatesOperations
  - Added operation group SourceControlOperations
  - Added operation group SourceControlsOperations
  - Added operation group ThreatIntelligenceIndicatorMetricsOperations
  - Added operation group ThreatIntelligenceIndicatorOperations
  - Added operation group ThreatIntelligenceIndicatorsOperations
  - Added operation group WatchlistItemsOperations
  - Added operation group WatchlistsOperations
  - Model AADDataConnector has a new parameter system_data
  - Model AATPDataConnector has a new parameter system_data
  - Model ASCDataConnector has a new parameter system_data
  - Model ActionRequest has a new parameter system_data
  - Model ActionResponse has a new parameter system_data
  - Model AlertRule has a new parameter system_data
  - Model AlertRuleTemplate has a new parameter system_data
  - Model AwsCloudTrailDataConnector has a new parameter system_data
  - Model Bookmark has a new parameter entity_mappings
  - Model Bookmark has a new parameter event_time
  - Model Bookmark has a new parameter query_end_time
  - Model Bookmark has a new parameter query_start_time
  - Model Bookmark has a new parameter system_data
  - Model Bookmark has a new parameter tactics
  - Model Bookmark has a new parameter techniques
  - Model DataConnector has a new parameter system_data
  - Model FusionAlertRule has a new parameter scenario_exclusion_patterns
  - Model FusionAlertRule has a new parameter source_settings
  - Model FusionAlertRule has a new parameter system_data
  - Model FusionAlertRule has a new parameter techniques
  - Model FusionAlertRuleTemplate has a new parameter last_updated_date_utc
  - Model FusionAlertRuleTemplate has a new parameter source_settings
  - Model FusionAlertRuleTemplate has a new parameter system_data
  - Model FusionAlertRuleTemplate has a new parameter techniques
  - Model Incident has a new parameter provider_incident_id
  - Model Incident has a new parameter provider_name
  - Model Incident has a new parameter system_data
  - Model Incident has a new parameter team_information
  - Model IncidentAdditionalData has a new parameter provider_incident_url
  - Model IncidentAdditionalData has a new parameter techniques
  - Model IncidentComment has a new parameter etag
  - Model IncidentComment has a new parameter last_modified_time_utc
  - Model IncidentComment has a new parameter system_data
  - Model IncidentOwnerInfo has a new parameter owner_type
  - Model MCASDataConnector has a new parameter system_data
  - Model MDATPDataConnector has a new parameter system_data
  - Model MicrosoftSecurityIncidentCreationAlertRule has a new parameter system_data
  - Model MicrosoftSecurityIncidentCreationAlertRuleTemplate has a new parameter last_updated_date_utc
  - Model MicrosoftSecurityIncidentCreationAlertRuleTemplate has a new parameter system_data
  - Model OfficeConsent has a new parameter consent_id
  - Model OfficeConsent has a new parameter system_data
  - Model OfficeDataConnector has a new parameter system_data
  - Model Operation has a new parameter is_data_action
  - Model Operation has a new parameter origin
  - Model Resource has a new parameter system_data
  - Model ResourceWithEtag has a new parameter system_data
  - Model ScheduledAlertRule has a new parameter alert_details_override
  - Model ScheduledAlertRule has a new parameter custom_details
  - Model ScheduledAlertRule has a new parameter entity_mappings
  - Model ScheduledAlertRule has a new parameter event_grouping_settings
  - Model ScheduledAlertRule has a new parameter incident_configuration
  - Model ScheduledAlertRule has a new parameter system_data
  - Model ScheduledAlertRule has a new parameter techniques
  - Model ScheduledAlertRule has a new parameter template_version
  - Model ScheduledAlertRuleCommonProperties has a new parameter alert_details_override
  - Model ScheduledAlertRuleCommonProperties has a new parameter custom_details
  - Model ScheduledAlertRuleCommonProperties has a new parameter entity_mappings
  - Model ScheduledAlertRuleCommonProperties has a new parameter event_grouping_settings
  - Model ScheduledAlertRuleProperties has a new parameter alert_details_override
  - Model ScheduledAlertRuleProperties has a new parameter custom_details
  - Model ScheduledAlertRuleProperties has a new parameter entity_mappings
  - Model ScheduledAlertRuleProperties has a new parameter event_grouping_settings
  - Model ScheduledAlertRuleProperties has a new parameter incident_configuration
  - Model ScheduledAlertRuleProperties has a new parameter techniques
  - Model ScheduledAlertRuleProperties has a new parameter template_version
  - Model ScheduledAlertRuleTemplate has a new parameter alert_details_override
  - Model ScheduledAlertRuleTemplate has a new parameter custom_details
  - Model ScheduledAlertRuleTemplate has a new parameter entity_mappings
  - Model ScheduledAlertRuleTemplate has a new parameter event_grouping_settings
  - Model ScheduledAlertRuleTemplate has a new parameter last_updated_date_utc
  - Model ScheduledAlertRuleTemplate has a new parameter system_data
  - Model ScheduledAlertRuleTemplate has a new parameter techniques
  - Model ScheduledAlertRuleTemplate has a new parameter version
  - Model Settings has a new parameter system_data
  - Model TIDataConnector has a new parameter system_data
  - Model TIDataConnector has a new parameter tip_lookback_period

**Breaking changes**

  - Model OfficeConsent no longer has parameter tenant_name
  - Model OfficeDataConnectorDataTypes has a new required parameter teams
  - Parameter alerts of model AlertsDataTypeOfDataConnector is now required
  - Parameter alerts of model MCASDataConnectorDataTypes is now required
  - Parameter exchange of model OfficeDataConnectorDataTypes is now required
  - Parameter exchange of model OfficeDataConnectorDataTypes is now required
  - Parameter indicators of model TIDataConnectorDataTypes is now required
  - Parameter indicators of model TIDataConnectorDataTypes is now required
  - Parameter logs of model AwsCloudTrailDataConnectorDataTypes is now required
  - Parameter logs of model AwsCloudTrailDataConnectorDataTypes is now required
  - Parameter share_point of model OfficeDataConnectorDataTypes is now required
  - Parameter share_point of model OfficeDataConnectorDataTypes is now required
  - Parameter state of model AwsCloudTrailDataConnectorDataTypesLogs is now required
  - Parameter state of model DataConnectorDataTypeCommon is now required
  - Parameter state of model OfficeDataConnectorDataTypesExchange is now required
  - Parameter state of model OfficeDataConnectorDataTypesSharePoint is now required
  - Parameter state of model TIDataConnectorDataTypesIndicators is now required
  - Parameter tenant_id of model DataConnectorTenantId is now required
  - Parameter trigger_uri of model ActionRequestProperties is now required
  - Removed operation AlertRulesOperations.create_or_update_action
  - Removed operation AlertRulesOperations.delete_action
  - Removed operation AlertRulesOperations.get_action
  - Removed operation IncidentCommentsOperations.create_comment
  - Removed operation IncidentCommentsOperations.list_by_incident

## 1.0.0b1 (2020-11-10)

* Initial Release
