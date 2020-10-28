# Release History

## 1.0.0b1 (2020-10-13)

This is beta preview version.

This version uses a next-generation code generator that introduces important breaking changes, but also important new features (like unified authentication and async programming).

**General breaking changes**

- Credential system has been completly revamped:

  - `azure.common.credentials` or `msrestazure.azure_active_directory` instances are no longer supported, use the `azure-identity` classes instead: https://pypi.org/project/azure-identity/
  - `credentials` parameter has been renamed `credential`

- The `config` attribute no longer exists on a client, configuration should be passed as kwarg. Example: `MyClient(credential, subscription_id, enable_logging=True)`. For a complete set of
  supported options, see the [parameters accept in init documentation of azure-core](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/core/azure-core/CLIENT_LIBRARY_DEVELOPER.md#available-policies)
- You can't import a `version` module anymore, use `__version__` instead
- Operations that used to return a `msrest.polling.LROPoller` now returns a `azure.core.polling.LROPoller` and are prefixed with `begin_`.
- Exceptions tree have been simplified and most exceptions are now `azure.core.exceptions.HttpResponseError` (`CloudError` has been removed).
- Most of the operation kwarg have changed. Some of the most noticeable:

  - `raw` has been removed. Equivalent feature can be found using `cls`, a callback that will give access to internal HTTP response for advanced user
  - For a complete set of
  supported options, see the [parameters accept in Request documentation of azure-core](https://github.com/Azure/azure-sdk-for-python/blob/master/sdk/core/azure-core/CLIENT_LIBRARY_DEVELOPER.md#available-policies)

**General new features**

- Type annotations support using `typing`. SDKs are mypy ready.
- This client has now stable and official support for async. Check the `aio` namespace of your package to find the async client.
- This client now support natively tracing library like OpenCensus or OpenTelemetry. See this [tracing quickstart](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk/core/azure-core-tracing-opentelemetry) for an overview.

## 0.48.0 (2020-09-22)

**Features**

  - Model SiteConfig has a new parameter acr_use_managed_identity_creds
  - Model SiteConfig has a new parameter acr_user_managed_identity_id
  - Model SiteConfigResource has a new parameter acr_use_managed_identity_creds
  - Model SiteConfigResource has a new parameter acr_user_managed_identity_id

## 0.47.0 (2020-06-03)

**Features**

  - Added operation WebAppsOperations.get_basic_publishing_credentials_policies
  - Added operation WebAppsOperations.update_scm_allowed
  - Added operation WebAppsOperations.update_ftp_allowed
  - Added operation WebAppsOperations.get_scm_allowed
  - Added operation WebAppsOperations.get_ftp_allowed

## 0.46.0 (2020-04-10)

**Features**

  - Model SiteConfig has a new parameter power_shell_version
  - Model SiteConfigResource has a new parameter power_shell_version
  - Added operation WebAppsOperations.get_private_endpoint_connection
  - Added operation WebAppsOperations.get_private_link_resources
  - Added operation WebAppsOperations.delete_private_endpoint_connection
  - Added operation WebAppsOperations.approve_or_reject_private_endpoint_connection

## 0.45.0 (2020-03-20)

**Features**

  - Added operation WebAppsOperations.list_host_keys
  - Added operation WebAppsOperations.sync_functions
  - Added operation WebAppsOperations.list_function_keys_slot
  - Added operation WebAppsOperations.sync_functions_slot
  - Added operation WebAppsOperations.delete_function_secret
  - Added operation WebAppsOperations.delete_host_secret_slot
  - Added operation WebAppsOperations.list_host_keys_slot
  - Added operation WebAppsOperations.delete_function_secret_slot
  - Added operation WebAppsOperations.create_or_update_host_secret
  - Added operation WebAppsOperations.list_sync_status
  - Added operation WebAppsOperations.list_sync_status_slot
  - Added operation WebAppsOperations.create_or_update_function_secret_slot
  - Added operation WebAppsOperations.list_function_keys
  - Added operation WebAppsOperations.create_or_update_host_secret_slot
  - Added operation WebAppsOperations.create_or_update_function_secret
  - Added operation WebAppsOperations.delete_host_secret
  - Added operation group StaticSitesOperations

## 0.44.0 (2019-11-08)

**Features**

  - Model EndpointDetail has a new parameter is_accessible
  - Model Identifier has a new parameter value
  - Model VirtualIPMapping has a new parameter service_name
  - Model SiteConfig has a new parameter health_check_path
  - Model SiteConfig has a new parameter pre_warmed_instance_count
  - Model SiteConfig has a new parameter api_management_config
  - Model CertificatePatchResource has a new parameter canonical_name
  - Model ValidateRequest has a new parameter container_image_platform
  - Model ValidateRequest has a new parameter
    container_registry_password
  - Model ValidateRequest has a new parameter
    container_image_repository
  - Model ValidateRequest has a new parameter container_image_tag
  - Model ValidateRequest has a new parameter
    container_registry_base_url
  - Model ValidateRequest has a new parameter
    container_registry_username
  - Model MetricSpecification has a new parameter
    supported_time_grain_types
  - Model FunctionEnvelope has a new parameter invoke_url_template
  - Model FunctionEnvelope has a new parameter is_disabled
  - Model FunctionEnvelope has a new parameter language
  - Model FunctionEnvelope has a new parameter test_data_href
  - Model GeoRegion has a new parameter org_domain
  - Model Certificate has a new parameter canonical_name
  - Model StackMajorVersion has a new parameter is_deprecated
  - Model StackMajorVersion has a new parameter is_hidden
  - Model StackMajorVersion has a new parameter is_preview
  - Model SiteConfigResource has a new parameter health_check_path
  - Model SiteConfigResource has a new parameter
    pre_warmed_instance_count
  - Model SiteConfigResource has a new parameter api_management_config
  - Model HostingEnvironmentDiagnostics has a new parameter
    diagnostics_output
  - Model AddressResponse has a new parameter type
  - Model AddressResponse has a new parameter id
  - Model AddressResponse has a new parameter name
  - Model AddressResponse has a new parameter kind
  - Added operation AppServiceEnvironmentsOperations.get_vip_info
  - Added operation WebAppsOperations.copy_production_slot
  - Added operation WebAppsOperations.list_site_backups
  - Added operation
    WebAppsOperations.get_app_setting_key_vault_reference
  - Added operation
    WebAppsOperations.get_app_settings_key_vault_references
  - Added operation WebAppsOperations.copy_slot_slot
  - Added operation WebAppsOperations.get_instance_info_slot
  - Added operation WebAppsOperations.get_instance_info
  - Added operation WebAppsOperations.list_site_backups_slot

**Breaking changes**

  - Operation
    WebAppsOperations.create_or_update_domain_ownership_identifier
    has a new signature
  - Operation
    WebAppsOperations.create_or_update_domain_ownership_identifier_slot
    has a new signature
  - Operation
    WebAppsOperations.update_domain_ownership_identifier_slot has a
    new signature
  - Operation WebAppsOperations.update_domain_ownership_identifier
    has a new signature
  - Model SitePatchResource no longer has parameter geo_distributions
  - Model Site no longer has parameter geo_distributions
  - Model EndpointDetail no longer has parameter is_accessable
  - Model ProcessThreadInfo no longer has parameter
    priviledged_processor_time
  - Model Identifier no longer has parameter identifier_id
  - Model SiteConfig no longer has parameter reserved_instance_count
  - Model SiteConfig no longer has parameter azure_storage_accounts
  - Model SiteConfigResource no longer has parameter
    reserved_instance_count
  - Model SiteConfigResource no longer has parameter
    azure_storage_accounts
  - Model HostingEnvironmentDiagnostics no longer has parameter
    diagnosics_output
  - Removed operation AppServicePlansOperations.list_metric_defintions
  - Removed operation AppServicePlansOperations.list_metrics
  - Removed operation
    WebSiteManagementClientOperationsMixin.validate_container_settings
  - Removed operation AppServiceEnvironmentsOperations.list_metrics
  - Removed operation
    AppServiceEnvironmentsOperations.list_worker_pool_instance_metrics
  - Removed operation
    AppServiceEnvironmentsOperations.list_multi_role_pool_instance_metrics
  - Removed operation
    AppServiceEnvironmentsOperations.list_multi_role_metrics
  - Removed operation AppServiceEnvironmentsOperations.list_vips
  - Removed operation
    AppServiceEnvironmentsOperations.list_web_worker_metrics
  - Removed operation
    AppServiceEnvironmentsOperations.list_metric_definitions
  - Removed operation WebAppsOperations.get_instance_process_thread
  - Removed operation WebAppsOperations.list_metrics
  - Removed operation WebAppsOperations.get_process_thread
  - Removed operation WebAppsOperations.list_hybrid_connection_keys
  - Removed operation WebAppsOperations.list_metric_definitions_slot
  - Removed operation WebAppsOperations.list_metrics_slot
  - Removed operation WebAppsOperations.get_process_thread_slot
  - Removed operation
    WebAppsOperations.list_hybrid_connection_keys_slot
  - Removed operation
    WebAppsOperations.get_instance_process_thread_slot
  - Removed operation WebAppsOperations.list_metric_definitions

## 0.43.1 (2019-10-17)

**General**

  - Fixed incorrectly generated multi-api package structure

## 0.43.0 (2019-10-01)

**Features**

  - Added operation group BillingMetersOperations
  - Added operation group WebSiteManagementClientOperationsMixin

**General**

  - Package is now multiapi

## 0.42.0 (2019-05-24)

**Features**

  - Model SitePatchResource has a new parameter identity
  - Model ManagedServiceIdentity has a new parameter
    user_assigned_identities
  - Model CloningInfo has a new parameter source_web_app_location
  - Added operation
    AppServiceEnvironmentsOperations.get_inbound_network_dependencies_endpoints
  - Added operation
    AppServiceEnvironmentsOperations.get_outbound_network_dependencies_endpoints
  - Added operation DeletedWebAppsOperations.list_by_location
  - Added operation
    DeletedWebAppsOperations.get_deleted_web_app_by_location

**Breaking changes**

  - Model ManagedServiceIdentity has a new parameter
    user_assigned_identities (renamed from identity_ids)

## 0.41.0 (2019-02-13)

**Features**

  - Model DeletedAppRestoreRequest has a new parameter
    use_dr_secondary
  - Model StackMinorVersion has a new parameter
    is_remote_debugging_enabled
  - Model IpSecurityRestriction has a new parameter subnet_traffic_tag
  - Model IpSecurityRestriction has a new parameter vnet_traffic_tag
  - Model IpSecurityRestriction has a new parameter
    vnet_subnet_resource_id
  - Model DeletedSite has a new parameter geo_region_name
  - Model SnapshotRestoreRequest has a new parameter use_dr_secondary
  - Model SiteAuthSettings has a new parameter
    client_secret_certificate_thumbprint
  - Model SiteConfig has a new parameter
    scm_ip_security_restrictions_use_main
  - Model SiteConfig has a new parameter scm_ip_security_restrictions
  - Model CorsSettings has a new parameter support_credentials
  - Model SiteConfigResource has a new parameter
    scm_ip_security_restrictions_use_main
  - Model SiteConfigResource has a new parameter
    scm_ip_security_restrictions
  - Model StackMajorVersion has a new parameter application_insights
  - Model AppServicePlanPatchResource has a new parameter
    maximum_elastic_worker_count
  - Model AppServicePlan has a new parameter
    maximum_elastic_worker_count
  - Model SitePatchResource has a new parameter geo_distributions
  - Model SitePatchResource has a new parameter
    in_progress_operation_id
  - Model SitePatchResource has a new parameter
    client_cert_exclusion_paths
  - Model SitePatchResource has a new parameter redundancy_mode
  - Model Site has a new parameter geo_distributions
  - Model Site has a new parameter in_progress_operation_id
  - Model Site has a new parameter client_cert_exclusion_paths
  - Model Site has a new parameter redundancy_mode
  - Model VnetInfo has a new parameter is_swift
  - Added operation WebAppsOperations.get_network_traces_slot_v2
  - Added operation
    WebAppsOperations.list_snapshots_from_dr_secondary_slot
  - Added operation WebAppsOperations.get_network_traces_slot
  - Added operation
    WebAppsOperations.start_web_site_network_trace_operation_slot
  - Added operation WebAppsOperations.get_network_trace_operation_v2
  - Added operation
    WebAppsOperations.start_web_site_network_trace_operation
  - Added operation WebAppsOperations.get_network_traces_v2
  - Added operation WebAppsOperations.stop_network_trace_slot
  - Added operation
    WebAppsOperations.get_network_trace_operation_slot_v2
  - Added operation
    WebAppsOperations.list_snapshots_from_dr_secondary
  - Added operation
    WebAppsOperations.get_network_trace_operation_slot
  - Added operation WebAppsOperations.stop_network_trace
  - Added operation WebAppsOperations.start_network_trace_slot
  - Added operation WebAppsOperations.get_network_trace_operation
  - Added operation WebAppsOperations.start_network_trace
  - Added operation WebAppsOperations.get_network_traces
  - Added operation
    RecommendationsOperations.list_recommended_rules_for_hosting_environment
  - Added operation
    RecommendationsOperations.list_history_for_hosting_environment
  - Added operation
    RecommendationsOperations.disable_all_for_hosting_environment
  - Added operation
    RecommendationsOperations.disable_recommendation_for_hosting_environment
  - Added operation
    RecommendationsOperations.reset_all_filters_for_hosting_environment
  - Added operation
    RecommendationsOperations.get_rule_details_by_hosting_environment

**Breaking changes**

  - Model AppServicePlanPatchResource no longer has parameter
    admin_site_name
  - Model AppServicePlan no longer has parameter admin_site_name

## 0.40.0 (2018-08-28)

**General Breaking changes**

This version uses a next-generation code generator that *might*
introduce breaking changes.

  - Model signatures now use only keyword-argument syntax. All
    positional arguments must be re-written as keyword-arguments. To
    keep auto-completion in most cases, models are now generated for
    Python 2 and Python 3. Python 3 uses the "*" syntax for
    keyword-only arguments.
  - Enum types now use the "str" mixin (class AzureEnum(str, Enum)) to
    improve the behavior when unrecognized enum values are encountered.
    While this is not a breaking change, the distinctions are important,
    and are documented here:
    <https://docs.python.org/3/library/enum.html#others> At a glance:
      - "is" should not be used at all.
      - "format" will return the string value, where "%s" string
        formatting will return `NameOfEnum.stringvalue`. Format syntax
        should be prefered.
  - New Long Running Operation:
      - Return type changes from
        `msrestazure.azure_operation.AzureOperationPoller` to
        `msrest.polling.LROPoller`. External API is the same.
      - Return type is now **always** a `msrest.polling.LROPoller`,
        regardless of the optional parameters used.
      - The behavior has changed when using `raw=True`. Instead of
        returning the initial call result as `ClientRawResponse`,
        without polling, now this returns an LROPoller. After polling,
        the final resource will be returned as a `ClientRawResponse`.
      - New `polling` parameter. The default behavior is
        `Polling=True` which will poll using ARM algorithm. When
        `Polling=False`, the response of the initial call will be
        returned without polling.
      - `polling` parameter accepts instances of subclasses of
        `msrest.polling.PollingMethod`.
      - `add_done_callback` will no longer raise if called after
        polling is finished, but will instead execute the callback right
        away.

**General Features**

  - Client class can be used as a context manager to keep the underlying
    HTTP session open for performance

**Features**

  - Model ValidateRequest has a new parameter is_xenon
  - Model SiteConfigResource has a new parameter
    reserved_instance_count
  - Model SiteConfigResource has a new parameter windows_fx_version
  - Model SiteConfigResource has a new parameter
    azure_storage_accounts
  - Model SiteConfigResource has a new parameter
    x_managed_service_identity_id
  - Model SiteConfigResource has a new parameter
    managed_service_identity_id
  - Model SiteConfigResource has a new parameter ftps_state
  - Model TriggeredWebJob has a new parameter web_job_type
  - Model CsmPublishingProfileOptions has a new parameter
    include_disaster_recovery_endpoints
  - Model SitePatchResource has a new parameter hyper_v
  - Model SitePatchResource has a new parameter is_xenon
  - Model StampCapacity has a new parameter is_linux
  - Model User has a new parameter scm_uri
  - Model SiteConfigurationSnapshotInfo has a new parameter snapshot_id
  - Model AppServiceEnvironmentPatchResource has a new parameter
    ssl_cert_key_vault_secret_name
  - Model AppServiceEnvironmentPatchResource has a new parameter
    has_linux_workers
  - Model AppServiceEnvironmentPatchResource has a new parameter
    ssl_cert_key_vault_id
  - Model BackupRequest has a new parameter backup_name
  - Model RecommendationRule has a new parameter id
  - Model RecommendationRule has a new parameter recommendation_name
  - Model RecommendationRule has a new parameter kind
  - Model RecommendationRule has a new parameter type
  - Model RecommendationRule has a new parameter category_tags
  - Model Site has a new parameter hyper_v
  - Model Site has a new parameter is_xenon
  - Model TriggeredJobRun has a new parameter web_job_id
  - Model TriggeredJobRun has a new parameter web_job_name
  - Model CertificateOrderAction has a new parameter action_type
  - Model SiteExtensionInfo has a new parameter
    installer_command_line_params
  - Model SiteExtensionInfo has a new parameter extension_id
  - Model SiteExtensionInfo has a new parameter extension_type
  - Model SiteAuthSettings has a new parameter validate_issuer
  - Model TriggeredJobHistory has a new parameter runs
  - Model ProcessInfo has a new parameter minidump
  - Model ProcessInfo has a new parameter total_cpu_time
  - Model ProcessInfo has a new parameter non_paged_system_memory
  - Model ProcessInfo has a new parameter working_set
  - Model ProcessInfo has a new parameter paged_memory
  - Model ProcessInfo has a new parameter private_memory
  - Model ProcessInfo has a new parameter user_cpu_time
  - Model ProcessInfo has a new parameter deployment_name
  - Model ProcessInfo has a new parameter peak_paged_memory
  - Model ProcessInfo has a new parameter peak_working_set
  - Model ProcessInfo has a new parameter peak_virtual_memory
  - Model ProcessInfo has a new parameter is_webjob
  - Model ProcessInfo has a new parameter privileged_cpu_time
  - Model ProcessInfo has a new parameter identifier
  - Model ProcessInfo has a new parameter paged_system_memory
  - Model ProcessInfo has a new parameter virtual_memory
  - Model ServiceSpecification has a new parameter log_specifications
  - Model ProcessThreadInfo has a new parameter identifier
  - Model ManagedServiceIdentity has a new parameter identity_ids
  - Model AppServicePlan has a new parameter
    free_offer_expiration_time
  - Model AppServicePlan has a new parameter hyper_v
  - Model AppServicePlan has a new parameter is_xenon
  - Model SiteConfig has a new parameter reserved_instance_count
  - Model SiteConfig has a new parameter windows_fx_version
  - Model SiteConfig has a new parameter azure_storage_accounts
  - Model SiteConfig has a new parameter
    x_managed_service_identity_id
  - Model SiteConfig has a new parameter managed_service_identity_id
  - Model SiteConfig has a new parameter ftps_state
  - Model WebJob has a new parameter web_job_type
  - Model Recommendation has a new parameter name
  - Model Recommendation has a new parameter id
  - Model Recommendation has a new parameter kind
  - Model Recommendation has a new parameter enabled
  - Model Recommendation has a new parameter type
  - Model Recommendation has a new parameter states
  - Model Recommendation has a new parameter category_tags
  - Model SlotConfigNamesResource has a new parameter
    azure_storage_config_names
  - Model SlotDifference has a new parameter level
  - Model AppServiceEnvironment has a new parameter
    ssl_cert_key_vault_secret_name
  - Model AppServiceEnvironment has a new parameter has_linux_workers
  - Model AppServiceEnvironment has a new parameter
    ssl_cert_key_vault_id
  - Model ContinuousWebJob has a new parameter web_job_type
  - Model AppServiceEnvironmentResource has a new parameter
    ssl_cert_key_vault_secret_name
  - Model AppServiceEnvironmentResource has a new parameter
    has_linux_workers
  - Model AppServiceEnvironmentResource has a new parameter
    ssl_cert_key_vault_id
  - Model AppServicePlanPatchResource has a new parameter
    free_offer_expiration_time
  - Model AppServicePlanPatchResource has a new parameter hyper_v
  - Model AppServicePlanPatchResource has a new parameter is_xenon
  - Model DeletedSite has a new parameter deleted_site_name
  - Model DeletedSite has a new parameter deleted_site_kind
  - Model DeletedSite has a new parameter kind
  - Model DeletedSite has a new parameter type
  - Model DeletedSite has a new parameter deleted_site_id
  - Added operation WebAppsOperations.put_private_access_vnet
  - Added operation
    WebAppsOperations.create_or_update_swift_virtual_network_connection
  - Added operation WebAppsOperations.update_azure_storage_accounts
  - Added operation WebAppsOperations.update_premier_add_on_slot
  - Added operation WebAppsOperations.get_container_logs_zip_slot
  - Added operation WebAppsOperations.discover_backup_slot
  - Added operation
    WebAppsOperations.update_swift_virtual_network_connection_slot
  - Added operation WebAppsOperations.get_private_access
  - Added operation WebAppsOperations.discover_backup
  - Added operation
    WebAppsOperations.create_or_update_swift_virtual_network_connection_slot
  - Added operation WebAppsOperations.delete_swift_virtual_network
  - Added operation WebAppsOperations.put_private_access_vnet_slot
  - Added operation WebAppsOperations.restore_from_deleted_app
  - Added operation WebAppsOperations.restore_from_backup_blob
  - Added operation
    WebAppsOperations.delete_swift_virtual_network_slot
  - Added operation WebAppsOperations.list_azure_storage_accounts
  - Added operation
    WebAppsOperations.list_azure_storage_accounts_slot
  - Added operation WebAppsOperations.restore_from_backup_blob_slot
  - Added operation
    WebAppsOperations.get_swift_virtual_network_connection
  - Added operation
    WebAppsOperations.get_swift_virtual_network_connection_slot
  - Added operation WebAppsOperations.get_container_logs_zip
  - Added operation WebAppsOperations.restore_snapshot
  - Added operation
    WebAppsOperations.update_swift_virtual_network_connection
  - Added operation WebAppsOperations.restore_snapshot_slot
  - Added operation WebAppsOperations.restore_from_deleted_app_slot
  - Added operation
    WebAppsOperations.update_azure_storage_accounts_slot
  - Added operation WebAppsOperations.get_private_access_slot
  - Added operation WebAppsOperations.update_premier_add_on
  - Added operation AppServiceEnvironmentsOperations.change_vnet
  - Added operation
    DiagnosticsOperations.list_site_detector_responses_slot
  - Added operation
    DiagnosticsOperations.get_site_detector_response_slot
  - Added operation DiagnosticsOperations.get_site_detector_response
  - Added operation
    DiagnosticsOperations.get_hosting_environment_detector_response
  - Added operation
    DiagnosticsOperations.list_site_detector_responses
  - Added operation
    DiagnosticsOperations.list_hosting_environment_detector_responses
  - Added operation
    RecommendationsOperations.disable_recommendation_for_subscription
  - Added operation
    RecommendationsOperations.disable_recommendation_for_site
  - Added operation group ResourceHealthMetadataOperations

**Breaking changes**

  - Operation RecommendationsOperations.get_rule_details_by_web_app
    has a new signature
  - Operation
    WebAppsOperations.list_publishing_profile_xml_with_secrets has
    a new signature
  - Operation
    WebAppsOperations.list_publishing_profile_xml_with_secrets_slot
    has a new signature
  - Operation WebAppsOperations.delete_slot has a new signature
  - Operation WebAppsOperations.delete has a new signature
  - Operation RecommendationsOperations.list_history_for_web_app has
    a new signature
  - Operation WebAppsOperations.update_slot has a new signature
  - Operation WebAppsOperations.create_or_update_slot has a new
    signature
  - Operation WebAppsOperations.create_or_update has a new signature
  - Operation WebAppsOperations.update has a new signature
  - Model TriggeredWebJob no longer has parameter
    triggered_web_job_name
  - Model TriggeredWebJob no longer has parameter job_type
  - Model SitePatchResource no longer has parameter snapshot_info
  - Model User no longer has parameter user_name
  - Model SiteConfigurationSnapshotInfo no longer has parameter
    site_configuration_snapshot_info_id
  - Model BackupRequest no longer has parameter backup_request_name
  - Model BackupRequest no longer has parameter backup_request_type
  - Model ResourceMetricDefinition no longer has parameter
    resource_metric_definition_id
  - Model ResourceMetricDefinition no longer has parameter
    resource_metric_definition_name
  - Model RecommendationRule no longer has parameter tags
  - Model SourceControl no longer has parameter source_control_name
  - Model Site no longer has parameter snapshot_info
  - Model VnetRoute no longer has parameter vnet_route_name
  - Model Certificate no longer has parameter geo_region
  - Model TriggeredJobRun no longer has parameter
    triggered_job_run_id
  - Model TriggeredJobRun no longer has parameter
    triggered_job_run_name
  - Model CertificateOrderAction no longer has parameter
    certificate_order_action_type
  - Model SiteExtensionInfo no longer has parameter
    site_extension_info_id
  - Model SiteExtensionInfo no longer has parameter installation_args
  - Model SiteExtensionInfo no longer has parameter
    site_extension_info_type
  - Model PremierAddOnOffer no longer has parameter
    premier_add_on_offer_name
  - Model TriggeredJobHistory no longer has parameter
    triggered_job_runs
  - Model ProcessInfo no longer has parameter total_processor_time
  - Model ProcessInfo no longer has parameter user_processor_time
  - Model ProcessInfo no longer has parameter
    peak_paged_memory_size64
  - Model ProcessInfo no longer has parameter
    privileged_processor_time
  - Model ProcessInfo no longer has parameter
    paged_system_memory_size64
  - Model ProcessInfo no longer has parameter process_info_name
  - Model ProcessInfo no longer has parameter peak_working_set64
  - Model ProcessInfo no longer has parameter virtual_memory_size64
  - Model ProcessInfo no longer has parameter mini_dump
  - Model ProcessInfo no longer has parameter is_web_job
  - Model ProcessInfo no longer has parameter private_memory_size64
  - Model ProcessInfo no longer has parameter
    nonpaged_system_memory_size64
  - Model ProcessInfo no longer has parameter working_set64
  - Model ProcessInfo no longer has parameter process_info_id
  - Model ProcessInfo no longer has parameter paged_memory_size64
  - Model ProcessInfo no longer has parameter
    peak_virtual_memory_size64
  - Model GeoRegion no longer has parameter geo_region_name
  - Model FunctionEnvelope no longer has parameter
    function_envelope_name
  - Model ProcessThreadInfo no longer has parameter
    process_thread_info_id
  - Model CloningInfo no longer has parameter ignore_quotas
  - Model AppServicePlan no longer has parameter
    app_service_plan_name
  - Model CertificatePatchResource no longer has parameter geo_region
  - Model WebJob no longer has parameter job_type
  - Model WebJob no longer has parameter web_job_name
  - Model Usage no longer has parameter usage_name
  - Model Deployment no longer has parameter deployment_id
  - Model Recommendation no longer has parameter tags
  - Model PremierAddOn no longer has parameter premier_add_on_tags
  - Model PremierAddOn no longer has parameter
    premier_add_on_location
  - Model PremierAddOn no longer has parameter premier_add_on_name
  - Model SlotDifference no longer has parameter slot_difference_type
  - Model ContinuousWebJob no longer has parameter
    continuous_web_job_name
  - Model ContinuousWebJob no longer has parameter job_type
  - Model TopLevelDomain no longer has parameter domain_name
  - Model AppServicePlanPatchResource no longer has parameter
    app_service_plan_patch_resource_name
  - Model MetricDefinition no longer has parameter
    metric_definition_name
  - Model PerfMonSample no longer has parameter core_count
  - Removed operation WebAppsOperations.recover
  - Removed operation WebAppsOperations.recover_slot
  - Removed operation
    WebAppsOperations.get_web_site_container_logs_zip
  - Removed operation
    WebAppsOperations.get_web_site_container_logs_zip_slot
  - Removed operation WebAppsOperations.discover_restore
  - Removed operation WebAppsOperations.discover_restore_slot
  - Model IpSecurityRestriction has a new signature

## 0.35.0 (2018-02-20)

**Breaking changes**

  - Many models signature changed to expose correctly required
    parameters. Example (non exhaustive) list:
      - AppServiceCertificateOrderPatchResource now requires
        product_type
      - AppServicePlanPatchResource now requires
        app_service_plan_patch_resource_name
      - CertificatePatchResource now requires password
      - DomainPatchResource now requires contact_admin,
        contact_billing, contact_registrant, contact_tech, consent
      - MigrateMySqlRequest now requires connection_string,
        migration_type
      - PushSettings now requires is_push_enabled
  - get_available_stacks now returns a pageable object

**Features**

  - Add certificate_registration_provider operations group
  - Add Diagnostics operations group
  - Add domain registration provider operations groups
  - All operations group have now a "models" attribute

## 0.34.1 (2017-10-24)

  - MSI fixes

## 0.34.0 (2017-10-16)

  - Add MSI support

## 0.33.0 (2017-10-04)

**Features**

  - Add providers.list_operations
  - Add verify_hosting_environment_vnet
  - Add web_apps.list_sync_function_triggers
  - Add web_apps.list_processes
  - Add web_apps.get_instance_process_module
  - Add web_apps.delete_process
  - Add web_apps.get_process_dump
  - Add web_apps continous web job operations
  - Add web_apps continous web job slots operations
  - Add web_apps public certificate operations
  - Add web_apps site_extension operations
  - Add web_apps functions operations
  - Add web_apps.list_function_secrets
  - Add web_apps.list_deployment_log
  - Add web_apps.list_deployment_log_slot
  - Add web_apps ms_deploy_status operations
  - Add web_apps ms_deploy_status_slot operations
  - Add web_apps ms_deploy_log_slot operations
  - Add web_apps instance_process_modules operations
  - Add web_apps instance_process_threads operations
  - Add web_apps instance_process_slot operations
  - Add web_apps instance_process_modules_slot operations
  - Add web_apps instance_process_threads_slot operations
  - Add web_apps.list_sync_function_triggers_slot
  - Add web_apps processes_slot operations
  - Add web_apps site_extensions_slot operations
  - Add web_apps triggered_web_jobs_slot operations
  - Add web_apps web_jobs_slot operations
  - Add web_apps triggered_web_jobs operations
  - Add web_apps web_jobs operations
  - Add web_apps.is_cloneable

**Breaking changes**

  - Remove 'name' and 'type' from several models (was ignored by server
    as read-only parameters)
  - Remove completely 'location' parameter from several models (None was
    the only acceptable value)
  - Remove a lot of incorrect parameter into DeletedSite
  - Remove deleted_web_apps.list_by_resource_group
  - Change web_apps.update_application_settings method signature
  - Change web_apps.update_connection_strings method signature
  - Change web_apps.update_metadata method signature
  - web_apps.recover now recover from a delete app to a previous
    snapshot
  - web_apps.recover_slot now recover from a delete app to a previous
    snapshot

## 0.32.0 (2017-04-26)

  - Support list web runtime stacks
  - Expose non resource based model type for SiteConfig,
    SiteAuthSettings, etc, to be used as property
  - Support list linux web available regions

## 0.31.1 (2017-04-20)

This wheel package is now built with the azure wheel extension

## 0.31.0 (2017-02-13)

  - Major refactoring and breaking changes
  - New API Version

## 0.30.0 (2016-10-17)

  - Initial release
