.. :changelog:

Release History
===============

0.4.0 (2019-04-05)
++++++++++++++++++

**Features**

- Added operation recovery_services.check_name_availability

0.3.0 (2018-05-25)
++++++++++++++++++

**Breaking Changes**

- Removed operation group BackupVaultConfigsOperations (moved to azure-mgmt-recoveryservicesbackup)
- Removed operation group BackupStorageConfigsOperations (moved to azure-mgmt-recoveryservicesbackup)

**Features**

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


0.2.0 (2017-10-16)
++++++++++++++++++

**Bugfixes**

* blob_duration is now a str (from iso-8601)
* "service_specification" is renamed "properties.service_specification"
* Fix operations list

0.1.1 (2019-03-12)
++++++++++++++++++

* Updating permissible versions of the msrestazure package to unblock `Azure/azure-cli#6973 <https://github.com/Azure/azure-cli/issues/6973>`_.

0.1.0 (2017-07-20)
++++++++++++++++++

* Initial Release
