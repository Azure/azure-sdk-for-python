# Release History

## 2.0.0b5 (2026-07-07)

### Features Added

  - Client `SelfHelpMgmtClient` added parameter `cloud_setting` in method `__init__`
  - Client `SelfHelpMgmtClient` added method `send_request`
  - Added model `ExtensionResource`

### Breaking Changes

  - This version introduces new hybrid models which have dual dictionary and model nature. Please follow https://aka.ms/azsdk/python/migrate/hybrid-models for migration.
  - Model `DiagnosticResource` moved instance variable `global_parameters`, `insights`, `accepted_at`, `provisioning_state` and `diagnostics` under property `properties` whose type is `DiagnosticResourceProperties`
  - Model `Filter` renamed its instance variable `values` to `values_property`
  - Model `SimplifiedSolutionsResource` moved instance variable `solution_id`, `parameters`, `title`, `appendix`, `content` and `provisioning_state` under property `properties` whose type is `SimplifiedSolutionsResourceProperties`
  - Model `SolutionMetadataResource` moved instance variable `solutions` under property `properties` whose type is `Solutions`
  - Model `SolutionNlpMetadataResource` moved instance variable `problem_title`, `problem_description`, `service_id`, `problem_classification_id`, `solutions` and `related_services` under property `properties` whose type is `NlpSolutions`
  - Model `SolutionPatchRequestBody` moved instance variable `trigger_criteria`, `parameters`, `solution_id`, `provisioning_state`, `title`, `content`, `replacement_maps` and `sections` under property `properties` whose type is `SolutionResourceProperties`
  - Model `SolutionResource` moved instance variable `trigger_criteria`, `parameters`, `solution_id`, `provisioning_state`, `title`, `content`, `replacement_maps` and `sections` under property `properties` whose type is `SolutionResourceProperties`
  - Model `SolutionResourceSelfHelp` moved instance variable `solution_id`, `title`, `content`, `replacement_maps` and `sections` under property `properties` whose type is `SolutionsResourcePropertiesSelfHelp`
  - Model `TroubleshooterResource` moved instance variable `solution_id`, `parameters`, `provisioning_state` and `steps` under property `properties` whose type is `TroubleshooterInstanceProperties`
  - Method `DiscoverySolutionOperations.list` changed its parameter `skiptoken` from `positional_or_keyword` to `keyword_only`

### Other Changes

  - Deleted model `DiscoveryResponse`/`OperationListResult` which actually were not used by SDK users

## 2.0.0b4 (2024-05-27)

### Features Added

  - Added operation CheckNameAvailabilityOperations.check_availability
  - Added operation group DiscoverySolutionNLPOperations

### Breaking Changes

  - Removed operation CheckNameAvailabilityOperations.post
  - Removed operation group DiscoverySolutionNLPSubscriptionScopeOperations
  - Removed operation group DiscoverySolutionNLPTenantScopeOperations

## 2.0.0b3 (2024-04-22)

### Features Added

  - Added operation SolutionOperations.warm_up
  - Added operation group DiscoverySolutionNLPSubscriptionScopeOperations
  - Added operation group DiscoverySolutionNLPTenantScopeOperations
  - Added operation group SimplifiedSolutionsOperations
  - Added operation group SolutionSelfHelpOperations
  - Model AutomatedCheckResult has a new parameter status
  - Model AutomatedCheckResult has a new parameter version
  - Model ResponseValidationProperties has a new parameter validation_scope
  - Model SolutionsDiagnostic has a new parameter estimated_completion_time
  - Model StepInput has a new parameter question_title

### Breaking Changes

  - Operation DiscoverySolutionOperations.list no longer has parameter scope

## 2.0.0b2 (2023-12-18)

### Features Added

  - Model SolutionPatchRequestBody has a new parameter content
  - Model SolutionPatchRequestBody has a new parameter parameters
  - Model SolutionPatchRequestBody has a new parameter provisioning_state
  - Model SolutionPatchRequestBody has a new parameter replacement_maps
  - Model SolutionPatchRequestBody has a new parameter sections
  - Model SolutionPatchRequestBody has a new parameter solution_id
  - Model SolutionPatchRequestBody has a new parameter title
  - Model SolutionPatchRequestBody has a new parameter trigger_criteria
  - Model SolutionResource has a new parameter content
  - Model SolutionResource has a new parameter parameters
  - Model SolutionResource has a new parameter provisioning_state
  - Model SolutionResource has a new parameter replacement_maps
  - Model SolutionResource has a new parameter sections
  - Model SolutionResource has a new parameter solution_id
  - Model SolutionResource has a new parameter system_data
  - Model SolutionResource has a new parameter title
  - Model SolutionResource has a new parameter trigger_criteria

### Breaking Changes

  - Model SolutionPatchRequestBody no longer has parameter properties
  - Model SolutionResource no longer has parameter properties

## 2.0.0b1 (2023-10-23)

### Features Added

  - Added operation group CheckNameAvailabilityOperations
  - Added operation group SolutionOperations
  - Added operation group TroubleshootersOperations
  - Model SolutionMetadataResource has a new parameter solutions

### Breaking Changes

  - Model SolutionMetadataResource no longer has parameter description
  - Model SolutionMetadataResource no longer has parameter required_parameter_sets
  - Model SolutionMetadataResource no longer has parameter solution_id
  - Model SolutionMetadataResource no longer has parameter solution_type
  - Removed operation DiagnosticsOperations.check_name_availability

## 1.0.0 (2023-06-25)

- First GA version


## 1.0.0b1 (2023-05-17)

* Initial Release
