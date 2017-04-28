.. :changelog:

Release History
===============

0.5.1 (2017-04-28)
++++++++++++++++++

**Bugfixes**

- Fix return exception in import/export

0.5.0 (2017-04-19)
++++++++++++++++++

**Breaking changes**

- `SqlManagementClient.list_operations` is now `SqlManagementClient.operations.list`

**New features**

- Added elastic pool capabilities to capabilities API.

**Notes**

* This wheel package is now built with the azure wheel extension

0.4.0 (2017-03-22)
++++++++++++++++++

Capabilities and security policy features.

Also renamed several types and operations for improved clarify and
consistency.

Additions:

* BlobAuditingPolicy APIs (e.g. databases.create_or_update_blob_auditing_policy)
* ThreatDetectionPolicy APIs (e.g. databases.create_or_update_threat_detection_policy)
* databases.list_by_server now supports $expand parameter
* Capabilities APIs (e.g. capabilities.list_by_location)

Classes and enums renamed:

* ServerFirewallRule -> FirewallRule
* DatabaseEditions -> DatabaseEdition
* ElasticPoolEditions -> ElasticPoolEdition
* ImportRequestParameters -> ImportRequest
* ExportRequestParameters -> ExportRequest
* ImportExportOperationResponse -> ImportExportResponse
* OperationMode -> ImportOperationMode
* TransparentDataEncryptionStates -> TransparentDataEncryptionStatus

Classes removed:

* Unused types: UpgradeHint, Schema, Table, Column

Operations renamed:

* servers.get_by_resource_group -> servers.get
* servers.create_or_update_firewall_rule -> firewall_rules.create_or_update, and similar for get, list, and delete
* databases.import -> databases.create_import_operation
* servers.import -> databases.import
* databases.pause_data_warehouse -> databases.pause
* databases.resume_data_warehouse -> databases.resume
* recommended_elastic_pools.list -> recommended_elastic_pools.list_by_server

Operations removed:

* Removed ImportExport operation results APIs since these are handled automatically by Azure async pattern.

0.3.3 (2017-03-14)
++++++++++++++++++

* Add database blob auditing and threat detection operations

0.3.2 (2017-03-08)
++++++++++++++++++

* Add import/export operations
* Expanded documentation of create modes

0.3.1 (2017-03-01)
++++++++++++++++++

* Added ‘filter’ param to list databases

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
