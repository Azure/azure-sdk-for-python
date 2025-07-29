# Release History

## 10.2.1 (2025-06-03)

### Other Changes

- Please note, this package has been deprecated and will no longer be maintained after 06/30/2024.
  Refer to [Azure Media Services retirement guide](https://learn.microsoft.com/azure/media-services/latest/azure-media-services-retirement) for more retirement details and how to migrate to the new services.
  Refer to our deprecation policy (https://aka.ms/azsdk/support-policies) for more details.

## 10.2.0 (2023-01-12)

### Features Added

  - Model Filters has a new parameter fade_in
  - Model Filters has a new parameter fade_out
  - Model StandardEncoderPreset has a new parameter experimental_options

## 10.2.0b1 (2022-12-27)

### Other Changes

  - Added generated samples in github repo
  - Drop support for python<3.7.0

## 10.1.0 (2022-09-14)

### Features Added

  - Added operation LiveEventsOperations.async_operation
  - Added operation LiveEventsOperations.operation_location
  - Added operation LiveOutputsOperations.async_operation
  - Added operation LiveOutputsOperations.operation_location
  - Added operation StreamingEndpointsOperations.async_operation
  - Added operation StreamingEndpointsOperations.operation_location
  - Model AudioTrack has a new parameter bit_rate
  - Model AudioTrack has a new parameter dash_settings
  - Model AudioTrack has a new parameter display_name
  - Model AudioTrack has a new parameter file_name
  - Model AudioTrack has a new parameter hls_settings
  - Model AudioTrack has a new parameter language_code
  - Model AudioTrack has a new parameter mpeg4_track_id
  - Model CommonEncryptionCbcs has a new parameter clear_key_encryption_configuration
  - Model CommonEncryptionCenc has a new parameter clear_key_encryption_configuration
  - Model ContentKeyPolicyPlayReadyLicense has a new parameter security_level
  - Model LiveOutput has a new parameter rewind_window_length

## 10.0.0 (2022-07-01)

**Features**

  - Added operation MediaservicesOperations.begin_create_or_update
  - Added operation MediaservicesOperations.begin_update
  - Added operation group MediaServicesOperationResultsOperations
  - Added operation group MediaServicesOperationStatusesOperations
  - Model MediaService has a new parameter private_endpoint_connections
  - Model MediaService has a new parameter provisioning_state
  - Model MediaServiceUpdate has a new parameter private_endpoint_connections
  - Model MediaServiceUpdate has a new parameter provisioning_state

**Breaking changes**

  - Removed operation MediaservicesOperations.create_or_update
  - Removed operation MediaservicesOperations.update

## 9.0.0 (2022-03-30)

**Features**

  - Added operation StreamingEndpointsOperations.skus
  - Added operation group OperationResultsOperations
  - Added operation group OperationStatusesOperations
  - Added operation group TracksOperations
  - Model H264Layer has a new parameter crf
  - Model H264Video has a new parameter rate_control_mode
  - Model H265Layer has a new parameter crf
  - Model StreamingEndpoint has a new parameter sku

**Breaking changes**

  - Model H264Layer no longer has parameter odata_type
  - Model H265Layer no longer has parameter odata_type
  - Model H265VideoLayer no longer has parameter odata_type
  - Model JpgLayer no longer has parameter odata_type
  - Model Layer no longer has parameter odata_type
  - Model PngLayer no longer has parameter odata_type
  - Model VideoLayer no longer has parameter odata_type

## 8.0.0 (2021-07-15)

**Features**

  - Model JobOutput has a new parameter preset_override
  - Model BuiltInStandardEncoderPreset has a new parameter configurations
  - Model MediaServiceIdentity has a new parameter user_assigned_identities
  - Model JobOutputAsset has a new parameter preset_override
  - Model MediaService has a new parameter public_network_access
  - Model MediaServiceUpdate has a new parameter public_network_access
  - Model StorageAccount has a new parameter status
  - Model StorageAccount has a new parameter identity
  - Model AccountEncryption has a new parameter status
  - Model AccountEncryption has a new parameter identity
  - Model LiveOutput has a new parameter system_data

**Breaking changes**

  - Model OperationCollection no longer has parameter odata_next_link

## 7.0.0 (2021-06-03)

**Features**

  - Model Asset has a new parameter system_data
  - Model StreamingPolicy has a new parameter system_data
  - Model Operation has a new parameter action_type
  - Model Operation has a new parameter is_data_action
  - Model JobInputAsset has a new parameter input_definitions
  - Model AccountFilter has a new parameter system_data
  - Model FaceDetectorPreset has a new parameter mode
  - Model FaceDetectorPreset has a new parameter blur_type
  - Model LiveEvent has a new parameter system_data
  - Model MediaService has a new parameter key_delivery
  - Model MediaService has a new parameter system_data
  - Model Job has a new parameter system_data
  - Model StreamingLocator has a new parameter system_data
  - Model StreamingEndpoint has a new parameter system_data
  - Model ContentKeyPolicy has a new parameter system_data
  - Model JobInputClip has a new parameter input_definitions
  - Model JobInputHttp has a new parameter input_definitions
  - Model MetricSpecification has a new parameter lock_aggregation_type
  - Model MetricSpecification has a new parameter supported_time_grain_types
  - Model MetricSpecification has a new parameter source_mdm_namespace
  - Model MetricSpecification has a new parameter source_mdm_account
  - Model MetricSpecification has a new parameter enable_regional_mdm_account
  - Model AssetFilter has a new parameter system_data
  - Model Transform has a new parameter system_data

**Breaking changes**

  - Removed operation MediaservicesOperations.get_by_subscription

## 7.0.0b1 (2020-12-01)

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

## 2.2.0 (2020-05-29)

**Features**

  - Added operation MediaservicesOperations.list_edge_policies

## 2.1.0 (2019-12-31)

**Features**

  - Model VideoAnalyzerPreset has a new parameter experimental_options
  - Model JobOutputAsset has a new parameter start_time
  - Model JobOutputAsset has a new parameter end_time
  - Model Job has a new parameter start_time
  - Model Job has a new parameter end_time
  - Model AudioAnalyzerPreset has a new parameter experimental_options
  - Model ContentKeyPolicyFairPlayConfiguration has a new parameter
    offline_rental_configuration
  - Model FaceDetectorPreset has a new parameter experimental_options
  - Model JobOutput has a new parameter start_time
  - Model JobOutput has a new parameter end_time

## 2.0.0 (2019-12-04)

**Features**

  - Model JobInputClip has a new parameter start
  - Model JobInputClip has a new parameter end
  - Model JobInputAsset has a new parameter start
  - Model JobInputAsset has a new parameter end
  - Model JobInputHttp has a new parameter start
  - Model JobInputHttp has a new parameter end

**General Breaking changes**

This version uses a next-generation code generator that might introduce
breaking changes if from some import. In summary, some modules were
incorrectly visible/importable and have been renamed. This fixed several
issues caused by usage of classes that were not supposed to be used in
the first place. AzureMediaServices cannot be imported from
azure.mgmt.media.azure_media_services anymore (import from
azure.mgmt.media works like before) AzureMediaServicesConfiguration
import has been moved from azure.mgmt.media.azure_media_services to
azure.mgmt.media A model MyClass from a "models" sub-module cannot be
imported anymore using azure.mgmt.media.models.my_class (import from
azure.mgmt.media.models works like before) An operation class
MyClassOperations from an operations sub-module cannot be imported
anymore using azure.mgmt.media.operations.my_class_operations (import
from azure.mgmt.media.operations works like before) Last but not least,
HTTP connection pooling is now enabled by default. You should always use
a client as a context manager, or call close(), or use no more than one
client per process.

## 1.1.1 (2018-03-26)

**Features**

  - Model StreamingLocator has a new parameter filters

**Bugfixes**

  - Parameter start of model JpgImage is now required
  - Parameter filename_pattern of model Mp4Format is now required
  - Parameter start of model Image is now required
  - Parameter input_label of model AudioOverlay is now required
  - Parameter input_label of model Overlay is now required
  - Parameter filename_pattern of model PngFormat is now required
  - Parameter bitrate of model H264Layer is now required
  - Parameter start of model PngImage is now required
  - Parameter bitrate of model VideoLayer is now required
  - Parameter formats of model StandardEncoderPreset is now required
  - Parameter codecs of model StandardEncoderPreset is now required
  - Parameter filename_pattern of model MultiBitrateFormat is now
    required
  - Parameter filename_pattern of model TransportStreamFormat is now
    required
  - Parameter filename_pattern of model Format is now required
  - Parameter filename_pattern of model ImageFormat is now required
  - Parameter filename_pattern of model JpgFormat is now required
  - Parameter input_label of model VideoOverlay is now required
  - Parameter labels of model OutputFile is now required

## 1.1.0 (2018-01-02)

**Bugfixes**

  - Operation JobsOperations.list has the correct list of optional
    parameters
  - Operation TransformsOperations.list has the correct list of optional
    parameters
  - Operation TransformsOperations.list has the correct list of optional
    parameters
  - Operation JobsOperations.list has the correct list of optional
    parameters

## 1.0.1 (2018-10-16)

**Bugfix**

  - Fix sdist broken in 1.0.0. No code change.

## 1.0.0 (2018-10-03)

**Features**

  - Model JobOutput has a new parameter label
  - Model StreamingLocatorContentKey has a new parameter
    label_reference_in_streaming_policy
  - Model Operation has a new parameter origin
  - Model Operation has a new parameter properties
  - Model VideoAnalyzerPreset has a new parameter insights_to_extract
  - Model LiveEventInput has a new parameter access_control
  - Model JobOutputAsset has a new parameter label
  - Added operation AssetsOperations.list_streaming_locators
  - Added operation JobsOperations.update
  - Added operation group AssetFiltersOperations
  - Added operation group AccountFiltersOperations

**Breaking changes**

  - Parameter scale_units of model StreamingEndpoint is now required
  - Model StreamingLocatorContentKey no longer has parameter label
  - Model VideoAnalyzerPreset no longer has parameter
    audio_insights_only
  - Model JobInput no longer has parameter label
  - Model JobInputs no longer has parameter label

API version endpoint is now 2018-07-01

**Note**

  - azure-mgmt-nspkg is not installed anymore on Python 3 (PEP420-based
    namespace package)

## 1.0.0rc2 (2018-07-19)

**Features**

  - Model LiveEventPreview has a new parameter alternative_media_id
  - Model StreamingLocator has a new parameter alternative_media_id
  - Model EnvelopeEncryption has a new parameter
    custom_key_acquisition_url_template
  - Model Job has a new parameter correlation_data

**Breaking changes**

  - Model EnvelopeEncryption no longer has parameter
    custom_license_acquisition_url_template

API version endpoint is now 2018-06-01-preview

## 1.0.0rc1 (2018-04-23)

**Disclaimer**

This is a complete rewriting of the package and a completly new RestAPI,
and no compatibility at all is possible.

API version endpoint is now 2018-03-30-preview

## 0.2.0 (2017-09-14)

**Bug fixes**

  - Fix deserialization issue with check_name_availability

**Features**

  - Adds operations.list

**Breaking changes**

  - Operations will now throw a ValidationError if input string is
    longer than 24 characters (not CloudError)
  - Some keyword arguments have been renamed "parameters"

## 0.1.2 (2016-06-27)

This wheel package is built with the azure wheel extension

## 0.1.1 (2016-12-12)

  - Best parameters check (you might experience exception change from
    CloudError to TypeError)
  - Delete account operation fix (random exception)
  - Create account operation fix (random exception)

## 0.1.0 (2016-11-07)

  - Initial preview release
