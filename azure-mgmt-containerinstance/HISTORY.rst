.. :changelog:

Release History
===============

1.0.0 (2018-06-13)
++++++++++++++++++

**Features**

- Model Container has a new parameter liveness_probe
- Model Container has a new parameter readiness_probe
- Model ContainerGroup has a new parameter diagnostics
- Model EnvironmentVariable has a new parameter secure_value
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

0.4.0 (2018-03-19)
++++++++++++++++++

**Breaking changes**

- container_groups.create_or_update is now a Long Running operation

**Features**

- New start_container operation group

0.3.1 (2018-02-05)
++++++++++++++++++

* Fix dnsnamelabel to dns_name_label

0.3.0 (2018-02-01)
++++++++++++++++++

* Add dnsnamelabel
* Add fqdn
* Add container_group_usage operation groups
* Add git_repo and secret to volumes
* Add container_groups.update

API version is now 2018-02-01-preview

0.2.0 (2017-10-20)
++++++++++++++++++

* Added on-failure/never container group retry policy
* Added container volumes mount support
* Added operations API
* Added container group instance view
* Renamed event class

0.1.0 (2017-07-27)
++++++++++++++++++

* Initial preview release
