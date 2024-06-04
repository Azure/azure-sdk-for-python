# Release History

## 1.0.0b5 (2023-10-23)

### Features Added

  - Model Event has a new parameter arg_query
  - Model Event has a new parameter event_sub_type
  - Model Event has a new parameter maintenance_id
  - Model Event has a new parameter maintenance_type
  - Model EventImpactedResource has a new parameter maintenance_end_time
  - Model EventImpactedResource has a new parameter maintenance_start_time
  - Model EventImpactedResource has a new parameter resource_group
  - Model EventImpactedResource has a new parameter resource_name
  - Model EventImpactedResource has a new parameter status

## 1.0.0b4 (2023-05-19)

### Features Added

  - Added operation EventsOperations.list_by_tenant_id
  - Added operation group EventOperations
  - Added operation group ImpactedResourcesOperations
  - Added operation group SecurityAdvisoryImpactedResourcesOperations
  - Model AvailabilityStatusProperties has a new parameter article_id
  - Model AvailabilityStatusProperties has a new parameter category
  - Model AvailabilityStatusProperties has a new parameter context
  - Model AvailabilityStatusProperties has a new parameter occured_time
  - Model AvailabilityStatusProperties has a new parameter title
  - Model AvailabilityStatusPropertiesRecentlyResolved has a new parameter unavailable_occured_time
  - Model AvailabilityStatusPropertiesRecentlyResolved has a new parameter unavailable_summary
  - Model EmergingIssuesGetResult has a new parameter system_data
  - Model Event has a new parameter additional_information
  - Model Event has a new parameter duration
  - Model Event has a new parameter external_incident_id
  - Model Event has a new parameter impact_type
  - Model Event has a new parameter reason
  - Model Event has a new parameter system_data
  - Model EventPropertiesArticle has a new parameter article_id
  - Model EventPropertiesArticle has a new parameter parameters
  - Model ImpactedServiceRegion has a new parameter impacted_tenants
  - Model MetadataEntity has a new parameter system_data
  - Model MetadataSupportedValueDetail has a new parameter resource_types
  - Model RecommendedAction has a new parameter action_url_comment
  - Model Resource has a new parameter system_data

### Breaking Changes

  - Client name is changed from `MicrosoftResourceHealth` to `ResourceHealthMgmtClient`
  - Model AvailabilityStatusProperties no longer has parameter occurred_time
  - Model AvailabilityStatusPropertiesRecentlyResolved no longer has parameter unavailability_summary
  - Model AvailabilityStatusPropertiesRecentlyResolved no longer has parameter unavailable_occurred_time
  - Operation EventsOperations.list_by_single_resource no longer has parameter view
  - Operation EventsOperations.list_by_subscription_id no longer has parameter view

## 1.0.0b3 (2023-02-16)

### Other Changes

  - Added generated samples in github repo
  - Drop support for python<3.7.0

## 1.0.0b2 (2022-11-15)

### Features Added

  - Added operation group EmergingIssuesOperations
  - Added operation group EventsOperations
  - Added operation group MetadataOperations
  - Model AvailabilityStatusProperties has a new parameter health_event_category
  - Model AvailabilityStatusProperties has a new parameter health_event_cause
  - Model AvailabilityStatusProperties has a new parameter health_event_id
  - Model AvailabilityStatusProperties has a new parameter health_event_type
  - Model AvailabilityStatusProperties has a new parameter occurred_time
  - Model AvailabilityStatusProperties has a new parameter recently_resolved

### Breaking Changes

  - Model AvailabilityStatusProperties no longer has parameter is_arm_resource
  - Model AvailabilityStatusProperties no longer has parameter occured_time
  - Model AvailabilityStatusProperties no longer has parameter recently_resolved_state

## 1.0.0b1 (2021-06-25)

* Initial Release
