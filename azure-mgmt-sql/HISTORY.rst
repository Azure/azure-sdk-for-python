.. :changelog:

Release History
===============

0.3.0 (2017-02-27)
++++++++++++++++++

**Breaking changes**

* Enums:

  * createMode renamed to CreateMode
  * Added ReadScale, SampleName, ServerState

* Added missing Database properties (failover_group_id, restore_point_in_time, read_scale, sample_name)
* Added missing ElasticPoolActivity properties (requested_*)
* Added missing ReplicationLink properties (is_termination_allowed, replication_mode)
* Added missing Server properties (external_administrator_*, state)
* Added operations APIs
* Removed unused Database.upgrade_hint property
* Removed unused RecommendedDatabaseProperties class
* Renamed incorrect RecommendedElasticPool.databases_property to databases
* Made firewall rule start/end ip address required
* Added missing kind property to many resources
* Many doc clarifications

0.2.0 (2016-12-12)
++++++++++++++++++

**Breaking changes**

* Parameters re-ordering (list_database_activity)
* Flatten create_or_update_firewall_rule from "parameters" to "start_ip_address" and "end_ip_address"

0.1.0 (2016-11-02)
++++++++++++++++++

* Initial Release
