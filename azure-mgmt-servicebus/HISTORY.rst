.. :changelog:

Release History
===============

0.4.1 (XXXXXXXXXX)
++++++++++++++++++

- Add dead_lettering_on_filter_evaluation_exceptions

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
