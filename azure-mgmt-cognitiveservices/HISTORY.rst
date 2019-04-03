.. :changelog:

Release History
===============

3.0.0 (2018-05-21)
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

- Add "resource_skus" operation group
- Update SKU list
- Add "accounts.get_usages" operation
- Client class can be used as a context manager to keep the underlying HTTP session open for performance

**Bugfixes**

- Compatibility of the sdist with wheel 0.31.0

2.0.0 (2017-10-26)
++++++++++++++++++

**Breaking changes**

- remove "location" as a constructor parameter
- sku_name in "check_sku_availability" result is now a str (from an enum)
- merge "cognitive_services_accounts" into "accounts" operation group
- "key_name" is now required to regenerate keys
- "location/skus/kind/type" are now required for "list" available skus

1.0.0 (2017-05-01)
++++++++++++++++++

* No changes, this is the 0.30.0 approved as stable.

0.30.0 (2017-05-01)
+++++++++++++++++++

* Initial Release (ApiVersion 2017-04-18)
* This wheel package is now built with the azure wheel extension