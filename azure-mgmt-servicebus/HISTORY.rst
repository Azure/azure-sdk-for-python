.. :changelog:

Release History
===============

0.5.1 (2018-07-09)
++++++++++++++++++

**Features**

- Add pending_replication_operations_count

**Bugfixes**

- Fix some Py3 import models

0.5.0 (2018-04-26)
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

**SDK Features**

- Client class can be used as a context manager to keep the underlying HTTP session open for performance

**ServiceBus features**

- Add dead_lettering_on_filter_evaluation_exceptions
- Add enable_batched_operations property to ServiceBus Queue
- Add migration_config operations
- Add skip and top to list commands
- Add 'properties' to CorrelationFilter
- Remove 'enableSubscriptionPartitioning' deprecated property

0.4.0 (2017-12-12)
++++++++++++++++++

**Features**

- Add alternate_name to some models (GEO DR pairing)
- Add disaster_recovery_configs.check_name_availability_method
- Add disaster_recovery_configs.list_authorization_rules
- Add disaster_recovery_configs.get_authorization_rule
- Add disaster_recovery_configs.list_keys

0.3.1 (2017-12-08)
++++++++++++++++++

**Bugfixes**

- Add missing forward_to, forward_dead_lettered_messages_to
- "rights" is now required, as expected, for operations called create_or_update_authorization_rule

0.3.0 (2017-10-26)
++++++++++++++++++

**Features**

- Add disaster_recovery_configs operation group
- Add regions operation group
- Add premium_messgings_regions operation group
- Add event_hubs operation group
- Add Geo DR

0.2.0 (2017-06-26)
++++++++++++++++++

* New API Version 2017-04-01
* Expect breaking changes, as a unstable client

This wheel package is built with the azure wheel extension

0.1.0 (2016-10-27)
++++++++++++++++++

* Initial Release
