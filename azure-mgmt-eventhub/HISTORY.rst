.. :changelog:

Release History
===============

1.2.0 (2017-12-12)
++++++++++++++++++

**Features**

- Add alternate_name to some models (GEO DR pairing)
- Add disaster_recovery_configs.check_name_availability
- Add disaster_recovery_configs.list_authorization_rules
- Add disaster_recovery_configs.get_authorization_rule
- Add disaster_recovery_configs.list_keys

**Bugfixes**

- "rights" is now required, as expected, for operations called create_or_update_authorization_rule
- Fix message_retention_in_days validation rule
- Fix partition_count validation rule

1.1.0 (2017-10-26)
++++++++++++++++++

**Features**

- Add disaster_recovery_configs operation group
- Add Geo DR

1.0.0 (2017-06-27)
++++++++++++++++++

* New API Version 2017-04-01
* Expect breaking changes, migrating from an unstable client

This wheel package is built with the azure wheel extension

0.2.0 (2016-10-27)
++++++++++++++++++

**Breaking changes**

* CreateOrUpdate has flatten its parameters, moving from one big Properties object to several small specifics.

0.1.0 (2016-10-27)
++++++++++++++++++

* Initial Release
