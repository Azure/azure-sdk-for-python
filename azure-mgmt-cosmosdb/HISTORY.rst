.. :changelog:

Release History
===============

0.4.1 (2018-05-15)
++++++++++++++++++

**Features**

- Add database_accounts.offline_region
- Add database_accounts.online_region
- Client class can be used as a context manager to keep the underlying HTTP session open for performance

0.4.0 (2018-04-17)
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

- Add VNet related properties to CosmosDB


0.3.1 (2018-02-01)
++++++++++++++++++

**Bugfixes**

- Fix capabilities model definition

0.3.0 (2018-01-30)
++++++++++++++++++

**Features**

- Add capability
- Add metrics operation groups

0.2.1 (2017-10-18)
++++++++++++++++++

**Bugfixes**

* Fix max_interval_in_seconds interval values from 1/100 to 5/86400
* Tags is now optional

**Features**

* Add operation list

0.2.0 (2017-06-26)
++++++++++++++++++

* Creation on this package based on azure-mgmt-documentdb 0.1.3 content
