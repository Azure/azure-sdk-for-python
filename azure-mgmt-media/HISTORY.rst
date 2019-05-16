.. :changelog:

Release History
===============

1.1.1 (2018-03-26)
++++++++++++++++++

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
- Parameter filename_pattern of model MultiBitrateFormat is now required
- Parameter filename_pattern of model TransportStreamFormat is now required
- Parameter filename_pattern of model Format is now required
- Parameter filename_pattern of model ImageFormat is now required
- Parameter filename_pattern of model JpgFormat is now required
- Parameter input_label of model VideoOverlay is now required
- Parameter labels of model OutputFile is now required

1.1.0 (2018-01-02)
++++++++++++++++++

**Bugfixes**

- Operation JobsOperations.list has the correct list of optional parameters
- Operation TransformsOperations.list has the correct list of optional parameters
- Operation TransformsOperations.list has the correct list of optional parameters
- Operation JobsOperations.list has the correct list of optional parameters

1.0.1 (2018-10-16)
++++++++++++++++++

**Bugfix**

- Fix sdist broken in 1.0.0. No code change.

1.0.0 (2018-10-03)
++++++++++++++++++

**Features**

- Model JobOutput has a new parameter label
- Model StreamingLocatorContentKey has a new parameter label_reference_in_streaming_policy
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
- Model VideoAnalyzerPreset no longer has parameter audio_insights_only
- Model JobInput no longer has parameter label
- Model JobInputs no longer has parameter label

API version endpoint is now 2018-07-01

**Note**

- azure-mgmt-nspkg is not installed anymore on Python 3 (PEP420-based namespace package)

1.0.0rc2 (2018-07-19)
+++++++++++++++++++++

**Features**

- Model LiveEventPreview has a new parameter alternative_media_id
- Model StreamingLocator has a new parameter alternative_media_id
- Model EnvelopeEncryption has a new parameter custom_key_acquisition_url_template
- Model Job has a new parameter correlation_data

**Breaking changes**

- Model EnvelopeEncryption no longer has parameter custom_license_acquisition_url_template

API version endpoint is now 2018-06-01-preview

1.0.0rc1 (2018-04-23)
+++++++++++++++++++++

**Disclaimer**

This is a complete rewriting of the package and a completly new RestAPI,
and no compatibility at all is possible.

API version endpoint is now 2018-03-30-preview

0.2.0 (2017-09-14)
++++++++++++++++++

**Bug fixes**

- Fix deserialization issue with check_name_availability

**Features**

- Adds operations.list

**Breaking changes**

- Operations will now throw a ValidationError if input string is longer than 24 characters (not CloudError)
- Some keyword arguments have been renamed "parameters"

0.1.2 (2016-06-27)
++++++++++++++++++

This wheel package is built with the azure wheel extension

0.1.1 (2016-12-12)
++++++++++++++++++

* Best parameters check (you might experience exception change from CloudError to TypeError)
* Delete account operation fix (random exception)
* Create account operation fix (random exception)

0.1.0 (2016-11-07)
++++++++++++++++++

* Initial preview release
