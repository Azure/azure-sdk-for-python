.. :changelog:

Release History
===============

2.0.0 (2018-05-23)
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

**Features**

- Client class can be used as a context manager to keep the underlying HTTP session open for performance

**Bugfixes**

- Scheduler jobs with basic authentication cannot be created (https://github.com/Azure/azure-sdk-for-node/issues/2347 for details)
- Compatibility of the sdist with wheel 0.31.0

1.1.3 (2017-09-07)
++++++++++++++++++

**Bug fixes**

- jobs.get function fails if custom retry policy is set (#1358)

1.1.2 (2017-04-18)
++++++++++++++++++

This wheel package is now built with the azure wheel extension

1.1.1 (2017-01-13)
++++++++++++++++++

* Fix `time_to_live` attribute type for correct parsing

1.1.0 (2016-11-14)
++++++++++++++++++

**breaking changes**

* Simplify `jobs.create_or_update` parameters
* Simplify `jobs.patch` parameters

1.0.0 (2016-08-30)
++++++++++++++++++

* Initial Release (API Version 2016-03-01)
