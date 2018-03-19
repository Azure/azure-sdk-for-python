.. :changelog:

Release History
===============

0.5.0 (2017-03-19)
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

- Fix invalid type of "top" in metrics.list operation

**Features**

- New operation group metric_baseline
- Add attribute action_group_resource itsm_receivers
- Add operation action_groups.update
- Add new parameter "metricnames" to metrics.list
- Add new parameter "metricnamespace" to metrics.list
- All operations group have now a "models" attribute

New ApiVersion version of metrics to 2018-01-01

0.4.0 (2017-10-25)
++++++++++++++++++

**Features**

- Merge into this package the "azure-monitor" package including following operations groups

  - event categories
  - activity log
  - tenant activity log
  - metrics definitions
  - metrics

- Adding new multi-dimensional metrics API

**Breaking changes**

- Some exceptions have moved from CloudError to ErrorResponseException
- "service_diagnostic_settings" renamed to "diagnostic_settings"

- Update API version of "metrics". Migrating from "azure-monitor" to "metrics" here needs to be rewritten.

**Bug fixes**

- Improving HTTP status code check for better exception

0.3.0 (2017-06-30)
++++++++++++++++++

**Features**

- Add action_groups operation group
- Add alert_rules.update method
- Add autoscale_settings.update method
- Add log_profiles.update method

**Breaking changes**

- activity_log_alerts.update has now flatten parameters "tags/enabled"

0.2.1 (2017-04-26)
++++++++++++++++++

* Removal of a REST endpoint not ready to release.

0.2.0 (2017-04-19)
++++++++++++++++++

* Add ActivityLogAlerts and DiagnosticSettings
* Minor improvements, might be breaking
* This wheel package is now built with the azure wheel extension

0.1.0 (2017-02-16)
++++++++++++++++++

* Initial Release
