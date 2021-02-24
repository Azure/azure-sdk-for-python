# Release History

## 3.1.0 (2021-02-24)

**Features**

  - Model MediaService has a new parameter system_data
  - Model MetricSpecification has a new parameter lock_aggregation_type
  - Model StreamingPolicy has a new parameter system_data
  - Model AssetFilter has a new parameter system_data
  - Model LiveEvent has a new parameter system_data
  - Model ContentKeyPolicy has a new parameter system_data
  - Model FaceDetectorPreset has a new parameter blur_type
  - Model FaceDetectorPreset has a new parameter mode
  - Model Transform has a new parameter system_data
  - Model JobInputClip has a new parameter input_definitions
  - Model JobInputHttp has a new parameter input_definitions
  - Model AccountFilter has a new parameter system_data
  - Model Job has a new parameter system_data
  - Model JobInputAsset has a new parameter input_definitions
  - Model StreamingEndpoint has a new parameter system_data
  - Model StreamingLocator has a new parameter system_data
  - Model Asset has a new parameter system_data

## 3.0.0 (2020-10-19)

**Features**

  - Model Image has a new parameter sync_mode
  - Model ServiceSpecification has a new parameter log_specifications
  - Model AudioAnalyzerPreset has a new parameter mode
  - Model LiveEvent has a new parameter transcriptions
  - Model LiveEvent has a new parameter hostname_prefix
  - Model LiveEvent has a new parameter use_static_hostname
  - Model PngImage has a new parameter sync_mode
  - Model JpgImage has a new parameter sprite_column
  - Model JpgImage has a new parameter sync_mode
  - Model H264Video has a new parameter sync_mode
  - Model Video has a new parameter sync_mode
  - Model MediaService has a new parameter encryption
  - Model MediaService has a new parameter identity
  - Model MediaService has a new parameter storage_authentication
  - Model VideoAnalyzerPreset has a new parameter mode
  - Model LiveEventEncoding has a new parameter stretch_mode
  - Model LiveEventEncoding has a new parameter key_frame_interval
  - Added operation LiveEventsOperations.allocate
  - Added operation group PrivateEndpointConnectionsOperations
  - Added operation group PrivateLinkResourcesOperations

**Breaking changes**

  - Parameter location of model StreamingEndpoint is now required
  - Parameter location of model TrackedResource is now required
  - Parameter location of model LiveEvent is now required
  - Parameter location of model MediaService is now required
  - Model LiveEvent no longer has parameter vanity_url

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
