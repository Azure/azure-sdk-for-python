.. :changelog:

Release History
===============

0.8.1 (2019-05-13)
++++++++++++++++++

**Bugfixes**

- Re-shipping 0.8.0 with wheel 0.33.4 (https://github.com/pypa/wheel/issues/294)

0.8.0 (2019-05-10)
++++++++++++++++++

**Features**

- Model RoutingProperties has a new parameter enrichments
- Added operation group IotHubOperations

**Breaking changes**

- Model IotHubProperties no longer has parameter operations_monitoring_properties

0.7.0 (2018-12-14)
++++++++++++++++++

**Features**

- Model OperationDisplay has a new parameter description
- Model TestRouteInput has a new parameter twin
- Model IotHubProperties has a new parameter device_streams
- Model TestAllRoutesInput has a new parameter twin

**Breaking changes**

- Operation IotHubResourceOperations.test_route has a new signature
- Operation IotHubResourceOperations.test_all_routes has a new signature

0.6.0 (2018-08-27)
++++++++++++++++++

**Features**

- Model CertificatePropertiesWithNonce has a new parameter certificate
- Model CertificateProperties has a new parameter certificate
- Added operation IotHubResourceOperations.test_all_routes
- Added operation IotHubResourceOperations.test_route
- Added operation IotHubResourceOperations.get_endpoint_health
- Added operation group ResourceProviderCommonOperations
- Client class can be used as a context manager to keep the underlying HTTP session open for performance

0.5.0 (2018-04-17)
++++++++++++++++++

**General Breaking changes**

This version uses a next-generation code generator that *might* introduce breaking changes.

- Model signatures now use only keyword-argument syntax. All positional arguments must be re-written as keyword-arguments.
  To keep auto-completion in most cases, models are now generated for Python 2 and Python 3. Python 3 uses the "*" syntax for keyword-only arguments.
- Enum types now use the "str" mixin (class AzureEnum(str, Enum)) to improve the behavior when unrecognized enum values are encountered.
  While this is not a breaking change, the distinctions are important, and are documented here:
  https://docs.python.org/3/library/enum.html#others
  At a glance:

  - "is" should not be used at all.
  - "format" will return the string value, where "%s" string formatting will return `NameOfEnum.stringvalue`. Format syntax should be prefered.

- New Long Running Operation:

  - Return type changes from `msrestazure.azure_operation.AzureOperationPoller` to `msrest.polling.LROPoller`. External API is the same.
  - Return type is now **always** a `msrest.polling.LROPoller`, regardless of the optional parameters used.
  - The behavior has changed when using `raw=True`. Instead of returning the initial call result as `ClientRawResponse`,
    without polling, now this returns an LROPoller. After polling, the final resource will be returned as a `ClientRawResponse`.
  - New `polling` parameter. The default behavior is `Polling=True` which will poll using ARM algorithm. When `Polling=False`,
    the response of the initial call will be returned without polling.
  - `polling` parameter accepts instances of subclasses of `msrest.polling.PollingMethod`.
  - `add_done_callback` will no longer raise if called after polling is finished, but will instead execute the callback right away.

**Bugfixes**

- Compatibility of the sdist with wheel 0.31.0

**Features**

- Add new ApiVersion 2018-04-01


0.4.0 (2017-10-11)
++++++++++++++++++

**Features**

- New API version 2017-07-01. This is a backward compatible.
- Add "if_match" parameter when applicable
- Add certificates operation group
- Add list available operations method
- Add "storage_containers" attribute to RoutingEndpoints

0.3.0 (2017-06-13)
++++++++++++++++++

**Features**

- New API version 2017-01-19. This is a backward compatible.
- Adding "routing" information

0.2.2 (2017-04-20)
++++++++++++++++++

**Bugfixes**

- Fix possible deserialization error, but updating from dict<str, enumtype> to dict<str, str> when applicable

**Notes**

- This wheel package is now built with the azure wheel extension

0.2.1 (2016-12-16)
++++++++++++++++++

**Bugfixes**

* Fix #920 - Invalid return type for `list_event_hub_consumer_groups`

0.2.0 (2016-12-12)
++++++++++++++++++

**Bugfixes**

* Better parameters checking (change exception from CloudError to TypeError)
* Date parsing fix (incorrect None date)
* CreateOrUpdate random exception fix

0.1.0 (2016-08-12)
++++++++++++++++++

* Initial Release
