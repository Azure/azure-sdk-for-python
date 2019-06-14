.. :changelog:

Release History
===============

0.7.1 (2019-06-12)
++++++++++++++++++

**Bugfixes**

- Make mutable some attributes that were read-only by mistake (so they can be set on creation)

0.7.0 (2019-05-30)
++++++++++++++++++

**Features**

- Model OSProfile has a new parameter ssh_public_key
- Model HanaInstance has a new parameter partner_node_id
- Model HanaInstance has a new parameter provisioning_state
- Added operation HanaInstancesOperations.create
- Added operation HanaInstancesOperations.delete

0.6.0 (2019-05-20)
++++++++++++++++++

**Features**

- Adding new Skus to enums

0.5.1 (2019-04-26)
++++++++++++++++++

**Bugfixes**

- Fixing incorrect RestAPI description

0.5.0 (2019-04-15)
++++++++++++++++++

**Features**

- Added operation enable_monitoring

0.4.0 (2019-02-21)
++++++++++++++++++

**Features**

- Model HanaInstance has a new parameter hw_revision

0.3.2 (2019-01-29)
++++++++++++++++++

**Features**

- Add proximity_placement_group

0.3.1 (2019-01-24)
++++++++++++++++++

**Bugfixes**

- Fix restart operation

0.3.0 (2019-01-03)
++++++++++++++++++

**Features**

- Added operation HanaInstancesOperations.update

0.2.1 (2018-08-31)
++++++++++++++++++

**Features**

- Add restart operation

0.2.0 (2018-08-06)
++++++++++++++++++

**Features**

- Add power state to Hana instance
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

0.1.1 (2018-05-17)
++++++++++++++++++

- Update HanaHardwareTypeNamesEnum and HanaInstanceSizeNamesEnum
- Add os_disks to storage_profile

0.1.0 (2018-01-17)
++++++++++++++++++

* Initial Release
