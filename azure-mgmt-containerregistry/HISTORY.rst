.. :changelog:

Release History
===============

2.1.0 (2018-07-26)
++++++++++++++++++

**Features**

- Model OperationDefinition has a new parameter service_specification
- Model OperationDefinition has a new parameter origin
- Added operation RegistriesOperations.list_policies
- Added operation RegistriesOperations.update_policies

2.0.0 (2018-04-30)
++++++++++++++++++

**Features**

- Support for build steps/taks (ApiVersion 2018-02-01-preview)
- Support for Azure Profiles
- Client class can be used as a context manager to keep the underlying HTTP session open for performance

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

1.0.1 (2017-10-09)
++++++++++++++++++

* Rename Managed_Basic, Managed_Standard, Managed_Premium to Basic, Standard, Premium.

1.0.0 (2017-09-22)
++++++++++++++++++

* New default API version 2017-10-01.
* Remove support for API Version 2017-06-01-preview
* New support for managed registries with three Managed SKUs.
* New support for registry webhooks and replications.
* Rename Basic SKU to Classic SKU.

0.3.1 (2017-06-30)
++++++++++++++++++

* Support for registry SKU update (2017-06-01-preview)
* New listUsages API to get the quota usages for a container registry (2017-06-01-preview)

0.3.0 (2017-06-15)
++++++++++++++++++

* This package now supports an additional ApiVersion 2017-06-01-preview

0.2.1 (2017-04-20)
++++++++++++++++++

This wheel package is now built with the azure wheel extension

0.2.0 (2017-03-20)
++++++++++++++++++

* New ApiVersion 2017-03-01
* Update getCredentials to listCredentials to support multiple login credentials.
* Refine regenerateCredential to support regenerate the specified login credential.
* Add Sku to registry properties as a required property.
* Rename GetProperties to Get.
* Change CreateOrUpdate to Create, add registry create parameters.

0.1.1 (2016-12-12)
++++++++++++++++++

**Bugfixes**

* Fix random error on Create and Delete operation

0.1.0 (2016-11-04)
++++++++++++++++++

* Initial Release
