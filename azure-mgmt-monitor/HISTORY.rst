.. :changelog:

Release History
===============

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
